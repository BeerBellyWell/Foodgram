from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeReadOnlySerializer, FollowSerializer, FavoriteSerializer,
    ShopingCartSerializer, RecipeIngredient,IngredientAmountSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import (
    Follow, User
)
from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, ShopingCart, 
)
from .mixins import CreateDestroyViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecipeReadOnlySerializer
        return RecipeSerializer

    @action(methods=['POST', 'DELETE', ], detail=True)
    def favorite(self, request, pk=None):
        data = {
            'recipe': pk,
            'user': self.request.user.username,
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data)
        if request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, recipe=pk)
            favorite.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        data = {
            'recipe': pk,
            'user': self.request.user.username,
        }
        serializer = ShopingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data)
        if request.method == 'DELETE':
            shoping_cart = get_object_or_404(ShopingCart, recipe=pk)
            shoping_cart.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        pass

    


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [AllowAny]
    # queryset = Follow.objects.all()

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.follower.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowUnfollowViewSet(CreateDestroyViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.follower.get(id=self.kwargs.get('following_id'))
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer
    # queryset = Favorite.objects.all()

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.favorites.get(id=self.kwargs.get('recipe_id'))
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShoppingCartViewSet(ModelViewSet):
    serializer_class = ShopingCartSerializer
    # queryset = ShopingCart.objects.all()

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        user.user_shoping_cart.get(id=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


# class UserViewSet(ModelViewSet):
#     http_method_names = ['get', 'post', 'patch', 'delete', ]
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     # pagination_class = 
# 
#     def get_serializer_class(self):
#         if self.action in ('create', ):
#             return UserCreateSerializer
# 
#         return UserSerializer

