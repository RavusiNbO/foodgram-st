from . import serializers
from rest_framework.response import Response
from recipes import models
from recipes.models import Follow, Favorite, Cart
from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.decorators import (permission_classes as
                                       drf_permission_classes)
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
from io import StringIO, BytesIO
from django.http import FileResponse
from .permissions import RecipePermission
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    pagination_class = pagination.LimitOffsetPagination
    # permission_classes = (AuthorOrReading,)
    # Каким образом возможно избежать этих двух методов?
    # Если не переопределить метод get_permissions класса джосера,
    # то тест get_user_list будет возвращать 401 вне зависимости от того, что 
    # написано в кастомном пермишене, т.к. в джосере для этого запроса
    # установлен пермишен CurrentUserOrAdmin.

    def get_permissions(self):  
        if self.action in ["list", "retrieve", "create"]:  
            return [  
                permissions.AllowAny(),  
            ]  
        return [  
            permissions.IsAuthenticated(),  
        ] 

    def get_serializer_class(self):
        if self.action == 'avatar':
            return serializers.AvatarSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscriptions' or self.action == 'subscribe':
            return serializers.FoodgramUserWithRecipesSerializer
        if self.request.method == "POST":
            return UserCreateSerializer
        return serializers.FoodgramUserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def avatar(self, request, *args, **kwargs):
        user = request.user

        if request.method == "PUT":
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False, url_path="subscriptions")
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(follows_user__follower=user)
        page = self.paginate_queryset(queryset)
        serializier = self.get_serializer_class()(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(data=serializier.data)

    @action(methods=["POST", "DELETE"], detail=True, url_path="subscribe")
    def subscribe(self, request, id):
        follower = request.user
        user = get_object_or_404(User, pk=id)
        
        if request.method == "POST":
            follow, created = Follow.objects.get_or_create(
                follower=follower,
                user=user
            )
            if (not created or follower == user):
                raise exceptions.ValidationError(
                    '''Нельзя подписываться на себя 
                    так же как и нельзя подписаться два раза!'''
                )
            
            serializer = self.get_serializer_class()(
                user, context=self.get_serializer_context()
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        try: 
            obj = Follow.objects.get(follower=follower, user=user) 
        except ObjectDoesNotExist: 
            raise exceptions.ValidationError() 
        obj.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination
    permission_classes = [RecipePermission,]

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return serializers.AlterRecipeSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_delete_fav_cart(self, model, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        if not self.request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        if self.request.method == "POST":
            object, created = model.objects.get_or_create(
                user=self.request.user,
                recipe=recipe)
            if not created: 
                raise exceptions.ValidationError(
                    "Рецепт уже есть в корзине покупок!")

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
        except (ObjectDoesNotExist, TypeError):
            raise exceptions.ValidationError 
        object.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)

    @drf_permission_classes([permissions.IsAuthenticated])
    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk):
        return self.add_delete_fav_cart(Favorite, pk)

    @drf_permission_classes([permissions.IsAuthenticated])
    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        return self.add_delete_fav_cart(Cart, pk)
    
    @action(detail=True, methods=["get"], url_path="get-link")
    def get_short_link(self, request, pk=None):
        res = ''.join(
            request.build_absolute_uri().split("get-link")[0].split('/api'))

        return Response({
            "short-link": res,
        }, status=status.HTTP_200_OK)

    @drf_permission_classes([permissions.IsAuthenticated])
    @action(
        methods=["get"],
        detail=False,
        url_path="download_shopping_cart",
        renderer_classes=[
            CSVRenderer,
        ],
    )
    def download_shopping_cart(self, request):
        cart_items = request.user.carts.select_related(
            'recipe', 'recipe__author')
        
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        writer.writerow(
            [f"Список покупок ({datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([])
        
        writer.writerow(['№', 'Ингредиент', 'Количество', 'Единица измерения'])
        
        ingredients = {}
        recipes = set()
        
        for item in cart_items:
            recipes.add(
                f"{item.recipe.name} (автор: {item.recipe.author.username})")
            for product in item.recipe.products.all():
                key = (
                    product.ingredient.name,
                    product.ingredient.measurement_unit
                )
                ingredients[key] = ingredients.get(key, 0) + product.amount
        
        sorted_ingredients = sorted(ingredients.items(), key=lambda x: x[0][0])
        for idx, ((name, unit), amount) in enumerate(
            sorted_ingredients,
            start=1
        ):
            writer.writerow([idx, name.capitalize(), amount, unit])
        
        writer.writerow([])
        writer.writerow(["Рецепты:"])
        for recipe in sorted(recipes):
            writer.writerow([f"- {recipe}"])
        
        csv_buffer = BytesIO(buffer.getvalue().encode('utf-8'))
        
        return FileResponse(
            csv_buffer,
            content_type='text/csv',
            as_attachment=True,
            filename=f'shopping_list_{datetime.now().strftime("%Y%m%d")}.csv'
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter

