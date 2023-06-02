from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from api.views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    # ShoppingCartViewSet, # FavoriteViewSet,
    FollowViewSet, FollowUnfollowViewSet,
)


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'users/subscriptions',
    FollowViewSet, basename='subscriptions'
)


urlpatterns = [
    path('users/<int:id>/subscribe/', FollowUnfollowViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'})
    ),
    path('', include(router.urls), name='api'),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
