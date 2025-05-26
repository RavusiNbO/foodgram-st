from . import serializers
from rest_framework.response import Response
from recipes import models
from recipes.models import Follow, Favorite, Cart
from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
from rest_framework_csv.renderers import CSVRenderer
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter, IngredientFilter
from .paginators import PageLimitPagination
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import csv
from django.http import FileResponse
from .permissions import AuthorOrReading
import os
from tempfile import NamedTemporaryFile


User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (AuthorOrReading,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
    @action(methods=["get", "put", "patch", "delete"],
            detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=False,
            methods=["put", "delete"],
            url_path="me/avatar",
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated(
                "Пользователь не аутентифицирован")

        if request.method == "PUT":
            serializer = serializers.AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"],
            detail=False,
            url_path="subscriptions",
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(follows_user__follower=user)
        page = self.paginate_queryset(queryset)
        serializier = serializers.FoodgramUserWithRecipesSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(data=serializier.data)

    @action(methods=["POST", "DELETE"],
            detail=True,
            url_path="subscribe",
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        follower = request.user
        user = get_object_or_404(User, pk=id)
        
        if request.method == "POST":
            follow, created = Follow.objects.get_or_create(
                follower=follower,
                user=user
            )
            if (not created):
                raise exceptions.ValidationError(
                    f'Нельзя дважды на пользователя {user}!'
                )
            if (follower == user):
                raise exceptions.ValidationError(
                    'Нельзя подписываться на себя!'
                )
            serializer = serializers.FoodgramUserWithRecipesSerializer(
                user, context=self.get_serializer_context()
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        try: 
            obj = Follow.objects.get(follower=follower, user=user) 
        except ObjectDoesNotExist: 
            raise exceptions.ValidationError("Такая подписка не существует") 
        obj.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReading,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return serializers.ForReadRecipeSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_delete_fav_cart(self, model, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)

        if self.request.method == "POST":
            object, created = model.objects.get_or_create(
                user=self.request.user,
                recipe=recipe)
            if not created:
                raise exceptions.ValidationError(
                    f"Рецепт {recipe.name} в \
                          {model.__class__.__name__} уже есть!")

            new = object.recipe
            serializer = self.get_serializer_class()(
                new, context=self.get_serializer_context()
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        try: 
            object = model.objects.get( 
                recipe=recipe, 
                user=self.request.user 
            ) 
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(
                f"Рецепт {recipe.name} в \
                      {model.__class__.__name__} не существует!")
        object.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_delete_fav_cart(Favorite, pk)

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.add_delete_fav_cart(Cart, pk)
    
    @action(detail=True, methods=["get"], url_path="get-link")
    def get_short_link(self, request, pk=None):
        return Response({
            'short-link': request.build_absolute_uri(f'/r/{pk}/')
        })

    @action(
        methods=["get"],
        detail=False,
        url_path="download_shopping_cart",
        renderer_classes=[
            CSVRenderer,
        ],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart_items = request.user.carts.select_related(
            'recipe', 'recipe__author')
        
        with NamedTemporaryFile(mode='w+', suffix='.csv', 
                                delete=False, encoding='utf-8') as temp_file:
            writer = csv.writer(temp_file)
            
            writer.writerow([f"Список покупок \
                            ({datetime.now().strftime('%Y-%m-%d %H:%M')})"])
            writer.writerow([])
            
            writer.writerow(
                ['№', 'Ингредиент', 'Количество', 'Единица измерения'])
            
            ingredients = {}
            recipes = set()
            
            for item in cart_items:
                recipes.add(f"{item.recipe.name} \
                            (автор: {item.recipe.author.username})")
                for product in item.recipe.products.all():
                    key = (
                        product.ingredient.name,
                        product.ingredient.measurement_unit)
                    ingredients[key] = ingredients.get(key, 0) + product.amount
            
            sorted_ingredients = sorted(
                ingredients.items(), key=lambda x: x[0][0])
            for idx, ((name, unit), amount) in enumerate(
                    sorted_ingredients, start=1):
                writer.writerow([idx, name.capitalize(), amount, unit])
            
            writer.writerow([])
            writer.writerow(["Рецепты:"])
            for recipe in sorted(recipes):
                writer.writerow([f"- {recipe}"])
            
            temp_file_path = temp_file.name
        
        response = FileResponse(
            open(temp_file_path, 'rb'),
            content_type='text/csv',
            as_attachment=True,
            filename=f'shopping_list_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
        response.callback = lambda: os.unlink(temp_file_path)
        
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter

