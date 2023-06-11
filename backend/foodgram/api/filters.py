from django_filters import rest_framework as filter
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class NameFilterInFilter(filter.BaseInFilter, filter.CharFilter):
    pass


class RecipeFilter(filter.FilterSet):
    tags = filter.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = NameFilterInFilter(field_name='author__id', lookup_expr='in')
    is_favorited = filter.NumberFilter(
        field_name='resipes__user',
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filter.NumberFilter(
        field_name='shopping_cart__user',
        method='is_shopping_cart_filter'
    )

    class Meta:
        Model = Recipe
        fields = ('tags', 'author', )

    def is_favorited_filter(self, queryset, name, value):
        if value == 1:
            return queryset.filter(**{name: self.request.user})
        return queryset

    def is_shopping_cart_filter(self, queryset, name, value):
        if value == 1:
            return queryset.filter(**{name: self.request.user})
        return queryset


class IngredientSearchFilter(SearchFilter):
    search_param = ('name')
