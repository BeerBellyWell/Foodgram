from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeReadOnlySerializer, FollowSerializer, FavoriteSerializer,
    ShopingCartSerializer, RecipeIngredient, IngredientAmountSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from users.models import (
    Follow, User
)
from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, ShopingCart, 
)
from .filters import RecipeFilter
from .mixins import CreateDestroyViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    http_method_names = ('get', )


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = None
    search_fields = ('name',)
    http_method_names = ('get', )
    

class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    ordering = ('-created',)
    filterset_fields = ('author',)
    filterset_class = RecipeFilter

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
        recipes = ShopingCart.objects.filter(user=request.user.pk).values_list('recipe', flat=True)
        # print(recipes)
        ingredient_recipe = RecipeIngredient.objects.filter(
            recipe_id__in=recipes).order_by('ingredient')
        ingredients = {}
        for ingredient in ingredient_recipe:
            # print(ingredient.ingredient)
            if ingredient.ingredient in ingredients.keys():
                ingredients[ingredient.ingredient] += ingredient.amount
            else:
                ingredients[ingredient.ingredient] = ingredient.amount
        wishlist = []
        for key, value in ingredients.items():
            wishlist.append(f'{key.name} - {value} {key.measurement_unit} \n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        # response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.follower.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowUnfollowViewSet(CreateDestroyViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        following = self.kwargs.get('id')
        user = self.request.user.pk
        serializer = self.get_serializer(data={})
        serializer.is_valid(raise_exception=True)
        obj = get_object_or_404(Follow, following=following, user=user)
        return obj

    def perform_create(self, serializer):
        following = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer.save(user=self.request.user, following=following)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, ]

    # def get_queryset(self):
    #     user = get_object_or_404(User, username=self.request.user.username)
    #     return user.favorites.get(id=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('id'))
        serializer.save(user=self.request.user, recipe=recipe)


class ShoppingCartViewSet(ModelViewSet):
    serializer_class = ShopingCartSerializer
    permission_classes = [IsAuthenticated, ]


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

