from django.shortcuts import render
from rest_framework.views import APIView
from . import serializers
from rest_framework.response import Response
from . import models
from users.models import Follow, Favorite, PurchaseList
from rest_framework import generics, viewsets, filters, pagination, mixins
from rest_framework.decorators import action
from djoser.views import UserViewSet

class CustomUserViewSet(UserViewSet):
    pagination_class=pagination.LimitOffsetPagination

    def get_serializer(self):
        if self.action == 'update' or self.action == 'destroy':
            return serializers.AvatarSerializer
        return serializers.UserSerializer

    @action(methods=['put', 'delete'], detail=True)
    def avatar(self, request):
        if request.method.lower() == 'put':
            self.request.user.avatar = request.data.get('avatar')
        else:
            self.request.user.avatar = None
    


        
        
        

class RecipeView(generics.ListCreateAPIView):
    queryset=models.Recipe.objects.all()
    serializer_class=serializers.RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends=(filters.SearchFilter, )
    pagination_class=None
    search_fields=('name',)
    
class FollowViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):

    serializer_class = serializers.FollowSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(follower=self.request.user)
        return queryset
    
class FavoriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = serializers.FavoriteSerializer

    def get_queryset(self):
        queryset = Favorite.objects.filter(user=self.request.user)
        return queryset
    
class PurchaseListViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = serializers.PurchaseListSerializer

    def get_queryset(self):
        queryset = Favorite.objects.filter(user=self.request.user)
        return queryset
