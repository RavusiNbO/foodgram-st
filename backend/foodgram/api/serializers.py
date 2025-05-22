from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes import models
from recipes.models import Follow, Favorite, Cart
from django.core.files.base import ContentFile
import base64
from djoser.serializers import SetPasswordSerializer
from .validators import validate_not_empty
from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import UserCreateSerializer
from rest_framework import exceptions


User = get_user_model()


class FoodgramSetPasswordSerializer(SetPasswordSerializer): 
    class Meta: 
        fields = ["current_password", "new_password"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ["name", "measurement_unit", "id"]


class RecipeFollowCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ("id", "name", "cooking_time", "image")
        read_only_fields = fields


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


class FoodgramUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64Serializer(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "username",
            "last_name",
            "avatar", 
            "is_subscribed",
            "id",
        ]
        required_fields = [
            'password',
            'username',
            'email',
            'first_name',
            'last_name',
        ]

    def get_is_subscribed(self, obj): 
        request = self.context.get("request") 
        if request and request.user.is_authenticated: 
            return Follow.objects.filter( 
                follower=request.user, 
                user=obj).exists() 
        return False


class CreateFoodgramUserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        required=True,
        validators=[validate_not_empty],
        max_length=150
    )
    last_name = serializers.CharField(
        required=True,
        validators=[validate_not_empty], 
        max_length=150
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "username",
            "last_name",
            "id",
            "password"
        ]
        required_fields = fields

    def validate(self, data):
        if (models.User.objects.filter(username=data.get("username")).exists()
                or models.User.objects.filter(
                    email=data.get("email")).exists()):
            raise exceptions.ValidationError()
        return data


class FoodgramUserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta:
        model = User
        fields = (FoodgramUserSerializer.Meta.fields 
                  + ['recipes', 'recipes_count'])

    def get_recipes(self, obj): 
        request = self.context.get("request") 
        if not request: 
            return [] 
 
        recipes_limit = int(request.GET.get("recipes_limit", 10**10))
        recipes = models.Recipe.objects.filter(
            author=obj
        )[: int(recipes_limit)]
 
        return RecipeFollowCartSerializer(recipes, many=True).data 


class RecipeProductSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.ProductInRecipe
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeProductSerializer(
        many=True,
        required=True,
        source="products"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64Serializer(required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.Recipe
        fields = "__all__"

    def validate_ingredients(self, value):
        s = set()
        if value == []:
            raise serializers.ValidationError("Список игредиентов пуст!")
        for i in value:
            s.add(i["ingredient"].name)
        if len(value) != len(s):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться!"
            )
        return value

    def create_products(self, recipe, ingredients_data):
        models.ProductInRecipe.objects.bulk_create(
            [
                models.ProductInRecipe(
                    recipe=recipe,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                ) for ingredient_data in ingredients_data
            ]
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("products")
        recipe = super().create(validated_data)

        self.create_products(recipe, ingredients_data)

        return recipe

    def update(self, recipe, validated_data):
        if not self.context.get("request").user.is_authenticated:
            raise exceptions.NotAuthenticated()
        if self.context.get("request").user != recipe.author:
            raise exceptions.PermissionDenied()
        amount_set = self.context.get("request").data.get("ingredients")
        if not amount_set:
            raise exceptions.ValidationError()
        ingredients_data = validated_data.pop("products")
        recipe = super().update(recipe, validated_data)

        if ingredients_data is not None:
            recipe.products.all().delete()
        self.create_products(recipe, ingredients_data)

        return recipe

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Cart.objects.filter(user=request.user, recipe=obj).exists()
        return False
