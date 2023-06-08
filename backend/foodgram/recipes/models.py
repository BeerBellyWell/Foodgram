from django.db import models
from django.core.validators import MinValueValidator

from users.models import User
from foodgram.settings import AMOUNT_MIN, MIN_VALUE


class Ingredient(models.Model):
    '''Класс ингредиентов'''
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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    '''Класс тэгов'''
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

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    '''Класс рецептов'''
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
        blank=False,
        verbose_name="Теги",
        related_name='tags',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
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
        blank=False,
        null=False,
    )
    text = models.TextField(
        'Описание рецепта',
        max_length=255,
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        blank=False,
        null=False,
        validators=(MinValueValidator(MIN_VALUE), )
    )
    created = models.DateTimeField(
        'Дата создания рецепта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeTag(models.Model):
    '''Класс связыввающий рецепт-тэг'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'У {self.recipe} тэги: {self.tag}'


class RecipeIngredient(models.Model):
    '''Класс связывающий рецепт-игредиент'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipeingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        blank=False,
        null=False,
        validators=(MinValueValidator(AMOUNT_MIN), )
    )

    def __str__(self) -> str:
        return f'У {self.recipe} ингредиенты: {self.ingredient}'


class Favorite(models.Model):
    '''Класс избранный рецептов'''
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
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    '''Список покупок'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} добавил в список покупок {self.recipe}.'
