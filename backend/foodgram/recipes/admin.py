from django.contrib import admin

from recipes.models import (
    Tag, Recipe, Ingredient, RecipeTag,
    RecipeIngredient, Favorite, ShoppingCart,
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
    list_display = ('id', 'name', 'text', 'cooking_time', 'count_favorite')
    list_filter = ('author', 'name', 'tags')

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj.pk).count()


class IngredientAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline]
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name', )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
