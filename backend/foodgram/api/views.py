from api.serializers import (FavoriteSerializer, FollowSerializer,
                             IngredientSerializer, RecipeIngredient,
                             RecipeReadOnlySerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from .filters import RecipeFilter, IngredientSearchFilter
from .mixins import CreateDestroyViewSet
from .permissions import AuthorOrReadOnly, ReadOrAdminOnly


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = [ReadOrAdminOnly, ]
    http_method_names = ('get', )


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [ReadOrAdminOnly, ]
    pagination_class = None
    filter_backends = (IngredientSearchFilter, )
    filterset_fields = None
    search_fields = ('name', )
    http_method_names = ('get', )


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete', )
    permission_classes = [AuthorOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    ordering = ('-created',)
    filterset_fields = ('author',)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecipeReadOnlySerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete', ], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        data = {
            'recipe': pk,
            'user': self.request.user.username,
        }
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite, recipe=pk, user=self.request.user.pk
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk=None):
        data = {
            'recipe': pk,
            'user': self.request.user.username,
        }
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == 'DELETE':
            shopping_cart = get_object_or_404(ShoppingCart, recipe=pk)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        recipes = ShoppingCart.objects.filter(
            user=request.user.pk).values_list('recipe', flat=True)
        ingredient_recipe = RecipeIngredient.objects.filter(
            recipe_id__in=recipes).order_by('ingredient')
        ingredients = {}
        for ingredient in ingredient_recipe:
            if ingredient.ingredient in ingredients.keys():
                ingredients[ingredient.ingredient] += ingredient.amount
            else:
                ingredients[ingredient.ingredient] = ingredient.amount
        shopping_cart = []
        for key, value in ingredients.items():
            shopping_cart.append(
                f'{key.name} - {value} {key.measurement_unit} \n'
            )

        response = HttpResponse(shopping_cart, 'Content-Type: text/plain')
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
    permission_classes = [IsAuthenticated, ]

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
