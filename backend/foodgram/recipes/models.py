from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from django.shortcuts import get_object_or_404
from multiselectfield import MultiSelectField

from users.models import User


CHOICES = (
    ('Завтрак', 'Breakfast'),
    ('Обед', 'Lunch'),
    ('Ужин', 'Dinner'),
)


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=64,
        blank=False,
        null=False,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=10,
        blank=False,
        null=False,
    )

    def get_amount(self):
        amount = RecipeIngredient.objects.filter(ingredient=self.id)
        return amount

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=50,
        blank=False,
        null=False,
        unique=True,
        default='name'
    )
    color = models.CharField(
        'Цвет тега',
        max_length=16,
        blank=False,
        null=False,
        unique=True,
    )
    slug = models.SlugField(
        'Slug тега',
        max_length=50,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        # choices=CHOICES,
        blank=False,
        # null=False,
        verbose_name="Теги",
        related_name='tags',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        # blank=False,
        # null=False,
        verbose_name="Ингредиенты",
        related_name='ingredients',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=50,
        blank=False,
        null=False,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/',
        blank=True, # исправить на False
        null=True,  # исправить на False
    )
    text = models.TextField(
        'Описание рецепта',
        max_length=255,
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipeingredient'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        blank=False,
        null=False,
    )

    # def add_ingredient(self, recipe_id, name, amount): # УБРАТЬ?!
    #     ingredient = get_object_or_404(Ingredient, name=name)
    #     return self.objects.get_or_create(recipe_id=recipe_id,
    #                                       ingredient=ingredient, amount=amount)

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='resipes',
    )

    class Meta:
        constraints = ( # Не работает
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_recipe'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} добавил в избранное {self.recipe}'
    

class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shoping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shoping_cart',
    )

    def __str__(self) -> str:
        return f'{self.user} добавил в список покупок {self.recipe}.'

