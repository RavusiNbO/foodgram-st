from django.shortcuts import render
from rest_framework.views import APIView
from . import serializers
from rest_framework.response import Response
from . import models
from users.models import Follow, Favorite, PurchaseList
from rest_framework import generics, viewsets, filters, pagination, mixins
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework import status

class CustomUserViewSet(UserViewSet):
    pagination_class=pagination.LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'destroy':
            return serializers.AvatarSerializer
        return serializers.UserSerializer

    @action(detail=True, methods=['put', 'delete'], url_path='avatar')
    def avatar(self, request, pk=None):
        user = self.get_object()
        
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        elif request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
    


        
        
        

class RecipeView(generics.ListCreateAPIView):
    queryset=models.Recipe.objects.all()
    serializer_class=serializers.RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = models.Recipe.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)





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
