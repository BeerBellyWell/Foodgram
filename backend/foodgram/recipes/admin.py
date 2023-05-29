from django.contrib import admin

from recipes.models import (Tag, Recipe, Ingredient, RecipeTag,
    RecipeIngredient, Favorite, ShopingCart,
)

class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    list_diaplay = ('amount')


class TagAdmin(admin.ModelAdmin):
    inlines = [RecipeTagInline]
    list_display = ('id', 'name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeTagInline, RecipeIngredientsInline, ]
    list_display = ('id', 'name', 'text', 'cooking_time')


class IngredientAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline]
    list_display = ('id', 'name', 'measurement_unit',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShopingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShopingCart, ShopingCartAdmin)
