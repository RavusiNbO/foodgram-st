from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import permissions, authentication
from . import models
from users.models import Follow, Favorite, Cart
from django.core.files.base import ContentFile
import base64
from django.shortcuts import get_object_or_404, get_list_or_404
from djoser.serializers import SetPasswordSerializer


User = get_user_model()


class CustomSetPasswordSerializer(SetPasswordSerializer):
    class Meta:
        fields = ["current_password", "new_password"]


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=models.Amount.objects.all()
    )

    class Meta:
        model = models.Ingredient
        fields = ["name", "measurement_unit", "amount"]


class CartRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ("id", "name", "cooking_time", "image")
        read_only_fields = ("id", "name", "cooking_time", "image")


class Base64Serializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64Serializer(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64Serializer(required=False)
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "username",
            "last_name",
            "avatar",
            "is_subscribed",
            'password',
            'id',
            'recipes'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'last_name': {'required': True},
            'first_name': {'required': True},
            'email': {'required': True},
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        

        if request and hasattr(request, 'path') and hasattr(request, 'method'):
            if request.path.endswith('/api/users/') and request.method == 'POST':
                self.fields.pop('avatar')
                self.fields.pop('is_subscribed')
            
            elif request.path.endswith('/api/users/subscriptions'):

            self.fields.pop('recipes')


            

    def get_author(self, obj):
        request = self.context.get('request')
        recipe_limit = request.query_params.get('recipe')
        if recipe_limit:
            queryset = 
    
    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, user=obj).exists()
        return False


class RecipeAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = models.Amount
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeUpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeAmountSerializer(
        many=True, required=True, read_only=False, source="amount_set"
    )
    image = Base64Serializer(required=False)

    class Meta:
        model = models.Recipe
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['author'].context['request'] = self.context['request']

    def update(self, obj, validated_data):
        ingredients_data = validated_data.pop("amount_set")
        obj.name = validated_data["name"]
        obj.text = validated_data["text"]
        obj.cooking_time = validated_data["cooking_time"]
        if "image" in validated_data:
            obj.image = validated_data["image"]
        obj.save()

        if ingredients_data is not None:
            obj.amount_set.all().delete()

            for ingredient_data in ingredients_data:

                models.Amount.objects.create(
                    recipe=obj,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                )
        return obj


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeAmountSerializer(
        many=True, required=True, read_only=False, source="amount_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64Serializer(required=True)

    class Meta:
        model = models.Recipe
        fields = "__all__"

    


    def create(self, validated_data):
        ingredients_data = validated_data.pop("amount_set")
        recipe = models.Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            models.Amount.objects.create(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            )
        return recipe

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Cart.objects.filter(user=request.user, recipe=obj).exists()
        return False
