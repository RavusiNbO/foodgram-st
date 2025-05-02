from . import serializers
from rest_framework.response import Response
from . import models
from users.models import Follow, Favorite, Cart
from rest_framework import viewsets, pagination, mixins
from rest_framework.decorators import action, permission_classes
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

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = pagination.LimitOffsetPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [
                permissions.AllowAny(),
            ]
        return [
            permissions.IsAuthenticated(),
        ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.action == "avatar":
            return serializers.AvatarSerializer
        elif self.action == "set_password":
            return serializers.CustomSetPasswordSerializer
        return serializers.UserSerializer

    @permission_classes([permissions.IsAuthenticated])
    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def avatar(self, request, *args, **kwargs):
        user = request.user

        if request.method == "PUT":
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @permission_classes([permissions.IsAuthenticated])
    @action(methods=["GET"], detail=False, url_path="subscriptions")
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(follow_user__follower=user)
        page = self.paginate_queryset(queryset)
        serializier = self.get_serializer_class()(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(data=serializier.data)

    @permission_classes([permissions.IsAuthenticated])
    @action(methods=["POST", "DELETE"], detail=True, url_path="subscribe")
    def subscribe(self, request, id):
        follower = request.user
        user = get_object_or_404(User, pk=id)
        if request.method == "POST":
            if (
                Follow.objects.filter(follower=follower, user=user).exists()
                or follower == user
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(follower=follower, user=user)
            serializer = self.get_serializer_class()(
                user, context=self.get_serializer_context()
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            try:
                obj = Follow.objects.get(follower=follower, user=user)
            except Follow.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action in [
            "Favorite",
            "shopping_cart",
            "download_shopping_cart",
        ] or self.request.method in ["POST", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == "Favorite":
            return serializers.RecipeFollowSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        if self.request.user != serializer.instance.author:
            raise exceptions.PermissionDenied()
        amount_set = self.request.data.get("ingredients")
        if not amount_set:
            raise exceptions.ValidationError()

    def perform_destroy(self, serializer):
        if not self.request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        if self.request.user != serializer.author:
            raise exceptions.PermissionDenied()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, *args, **kwargs):
        res = request.build_absolute_uri().split("get-link")[0]
        return Response({"short-link": res}, status=status.HTTP_200_OK)

    @permission_classes([permissions.IsAuthenticated])
    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def Favorite(self, request, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)

        if request.method == "POST":
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            fav = Favorite.objects.create(user=request.user, recipe=recipe)
            new = fav.recipe
            serializer = self.get_serializer_class()(
                new, context=self.get_serializer_context()
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        else:
            try:
                favorite = Favorite.objects.get(
                    recipe=recipe,
                    user=request.user
                )
            except Favorite.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @permission_classes([permissions.IsAuthenticated])
    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(models.Recipe, pk=pk)

        if request.method == "POST":
            if Cart.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.create(user=request.user, recipe=recipe)
            serializer = serializers.CartRecipeSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            try:
                cart = Cart.objects.get(recipe=recipe, user=request.user)
            except Cart.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @permission_classes([permissions.IsAuthenticated])
    @action(
        methods=["get"],
        detail=False,
        url_path="download_shopping_cart",
        renderer_classes=[
            CSVRenderer,
        ],
    )
    def download_shopping_cart(self, request):
        ingredients = Cart.objects.filter(user=request.user).values(
            "recipe__ingredients__name",
            "recipe__ingredients__measurement_unit",
            "recipe__amount__amount",
        )

        content = [
            {
                "name": i["recipe__ingredients__name"],
                "measurement_unit": i["recipe__ingredients__measurement_unit"],
                "amount": i["recipe__amount__amount"],
            }
            for i in ingredients
        ]

        return Response(content)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter
