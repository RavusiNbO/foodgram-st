from . import serializers
from rest_framework.response import Response
from . import models
from users.models import Follow, Favorite, Cart
from rest_framework import viewsets, filters, pagination, mixins
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_csv.renderers import CSVRenderer

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    pagination_class=pagination.LimitOffsetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request 
        return context

    def get_serializer_class(self):
        if self.action == 'avatar':
            return serializers.AvatarSerializer
        elif self.action == 'set_password':
            return serializers.CustomSetPasswordSerializer
        return serializers.UserSerializer

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request, *args, **kwargs):
        user = request.user
        
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        elif request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(methods=['GET'], detail=False, url_path="subscriptions")
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(follow_user__follower=user)
        page = self.pagination_class(queryset)
        serialzier = self.get_serializer_class()(page, many=True, context=self.get_serializer_context())
        return Response(data=serialzier.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST', 'DELETE'], detail=True, url_path="subscribe")
    def subscribe(self, request, id):
        follower = request.user
        user = get_object_or_404(User, pk=id)
        if request.method=='POST':
            if Follow.objects.filter(follower=follower, user=user).exists() or follower == user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(follower=follower, user=user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(Follow, follower=follower, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



    


        

class RecipeViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset=models.Recipe.objects.all()
    serializer_class=serializers.RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.RecipeUpdateSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
    @action(detail=True, methods=['get'], url_path="get-link")
    def get_ink(self, request, *args, **kwargs):
        res = request.build_absolute_uri().split('get-link')[0]
        return Response({'short-link':res}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def Favorite(self, request, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        
        if request.method == "POST":
            if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)

        else:
            favorite = get_object_or_404(Favorite, recipe=recipe, user=request.user)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)
        
        if request.method == "POST":
            if Cart.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            Cart.objects.create(user=request.user, recipe=recipe)
            serializer = serializers.CartRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            cart = get_object_or_404(Cart, recipe=recipe, user=request.user)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(methods=["get"], detail=False, url_path="download_shopping_cart", renderer_classes=[CSVRenderer,])
    def download_shopping_cart(self, request):
        objects = Cart.objects.filter(user=request.user)
        ingredients = (
        Cart.objects
        .filter(user=request.user)
        .values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
            'recipe__amount__amount'
        )
        )

        content = [
            {
                'name' : i['recipe__ingredients__name'],
                'measurement_unit' : i['recipe__ingredients__measurement_unit'],
                'amount' : i['recipe__amount__amount']
            }
            for i in ingredients
        ]
        del content[0]

        return Response(content)

    
        
    
    

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends=(filters.SearchFilter, )
    pagination_class=None
    search_fields=('name',)
    


    