from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import permissions, authentication
from . import models
from users.models import Follow, Favorite, PurchaseList
from django.core.files.base import ContentFile
import base64
from django.shortcuts import get_object_or_404
    
User=get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.PrimaryKeyRelatedField(
        queryset=models.Amount.objects.all()
    )

    class Meta:
        model=models.Ingredient
        fields=["name", "measurement_unit", "amount"]


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        required=True,
        write_only=True,
        queryset=Favorite.objects.all()
        )

    class Meta:
        model=Favorite
        fields=('id',)

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseList
        fields=('purchase_recipe__name', 'purchase_recipe__image', 'purchase_recipe__cooking_time')


class Base64Serializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    
class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64Serializer(required=True)

    class Meta:
        model=User
        fields = ('avatar',)

class UserSerializer(serializers.ModelSerializer):
    avatar = Base64Serializer(required=False)
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model=User
        fields=('email', 'first_name', 'username', 'last_name', 'avatar', 'id', 'is_subscribed')

        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user or None, 
                user=obj or None
            ).exists()
        return False


class RecipeAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=models.Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField(required=True)

    class Meta:
        model=models.Amount
        fields=["id", "amount"]

class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeAmountSerializer(many=True, required=True, read_only=False, source='amount_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64Serializer(required=True)
    
    class Meta:
        model=models.Recipe
        fields='__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('amount_set')
        recipe = models.Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            models.Amount.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(
            user=request.user, 
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return PurchaseList.objects.filter(
            user=request.user, 
            recipe=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model=Follow
        exclude=('follower',)