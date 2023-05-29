from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from api.views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, FavoriteViewSet, # SubscribeViewSet
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

# router.register(
#     'users/(?P<users_id>\d+)/subscribe', # users_id?
#     FollowUnfollowViewSet, basename='subscribe'
# )
router.register(
    r'recipes/download_shopping_cart',
    ShoppingCartViewSet, basename='download_shopping_cart'
)
# router.register(
#     r'recipes/(?P<recipes_id>\d+)/favorite',
#     FavoriteViewSet, basename='favorites'
# )


urlpatterns = [
    path('users/<int:id>/subscribe/', FollowUnfollowViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    # path('users/subscriptions/', SubscribeViewSet.as_view({'get': 'list'})),
    path('', include(router.urls), name='api'),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include ('djoser.urls.authtoken')),
]

