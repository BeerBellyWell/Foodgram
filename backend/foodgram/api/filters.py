from django_filters import rest_framework as filter

from recipes.models import Recipe


class NameFilterInFilter(filter.BaseInFilter, filter.CharFilter):
    pass


class RecipeFilter(filter.FilterSet):
    # genre = SlugFilterInFilter(field_name='genre__slug', lookup_expr='in')
    # category = SlugFilterInFilter(field_name='category__slug',
    #                               lookup_expr='in')
    # name = SlugFilterInFilter(field_name='name', lookup_expr='in')
    # year = filter.BaseInFilter(field_name='year', lookup_expr='in')
    tags = NameFilterInFilter(field_name='tags__name', lookup_expr='in')
    author = NameFilterInFilter(field_name='author__first_name', lookup_expr='in')
    is_favorited = filter.BaseInFilter(field_name='is_favorited', lookup_expr='in')

    class Meta:
        Model = Recipe
        fields = ['tags', 'author', 'is_favorited']