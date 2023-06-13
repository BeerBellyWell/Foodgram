from django.contrib import admin
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import User


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    list_display = ('amount', )


class TagAdmin(admin.ModelAdmin):
    inlines = [RecipeTagInline]
    list_display = ('id', 'name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeTagInline, RecipeIngredientsInline, ]
    list_display = ('id', 'name', 'text', 'cooking_time', 'count_favorite', )
    list_filter = ('tags', )
    search_fields= ('name', 'author__username', 'author__email', )

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj.pk).count()


class IngredientAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline]
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('measurement_unit', )
    search_fields = ('name', )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags', )
    search_fields = ('user__username', 'user__email', 'recipe__name', )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags', )
    search_fields = ('user__username', 'user__email', 'recipe__name', )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', )
    list_filter = ('recipe__tags', )
    search_fields = (
        'recipe__name', 'recipe__author__username', 'recipe__author__email'
    )


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag', )
    search_fields = ('recipe__name', 'tag__name', )


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
