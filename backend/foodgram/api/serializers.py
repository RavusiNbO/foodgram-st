from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import permissions, authentication
from . import models
from users.models import Follow, Favorite, PurchaseList
from django.core.files.base import ContentFile
import base64
    
User=get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.PrimaryKeyRelatedField(
        queryset=models.Amount.objects.all(),
        many=True
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
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    
class AvatarSerializer(serializers.Serializer):
    avatar = Base64Serializer(required=True)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('email', 'first_name', 'username', 'last_name')

class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer()
    class Meta:
        model=models.Recipe
        fields='__all__'

class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model=Follow
        exclude=('follower',)