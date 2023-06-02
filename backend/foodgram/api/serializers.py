import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user_id = self.context.get('request').user.pk
        return Follow.objects.filter(following=obj.pk, user=user_id).exists()

    def create(self, validated_data):
        password = validated_data.get('password')
        validated_data['password'] = make_password()
        data = super(UserSerializer, self).create(validated_data)
        data.password = password
        return data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'following': {'required': False},
        }

    def _get_recipes_limit(self):
        recipes = self.context.get('request').query_params.get('recipes_limit')
        recipes_limit = int(recipes)
        return recipes_limit

    def validate(self, data):
        following_id = self.context.get('view').kwargs.get('id')
        following = get_object_or_404(User, pk=following_id)
        user = self.context.get('request').user
        is_follow = user.follower.filter(following=following_id)
        method = self.context.get('request').method

        if user == following and method == 'POST':
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        elif is_follow and method == 'POST':
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        data = {'following': following, 'user': user}
        return data

    def to_representation(self, obj):
        recipes_limit = self._get_recipes_limit()
        data = UserSerializer(obj.following, context={'request': obj}).data
        recipes = Recipe.objects.filter(author=data['id'])
        count = recipes.count()
        data_2 = ResponseShoppingCartSerializer(
            recipes[:recipes_limit], many=True).data
        data['recipes'] = data_2
        data['recipes_count'] = count
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='id',
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        read_only_fields = ('user',)

    def to_representation(self, obj):
        return ResponseShoppingCartSerializer(obj.recipe).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )
        extra_kwargs = {
            'name': {'read_only': True},
            'measurement_unit': {'read_only': True},
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ['recipe', 'ingredient', 'amount']


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeTag
        fields = ['recipe', 'tag']


class IngredientAmountSerializer(serializers.Serializer):

    amount = serializers.IntegerField(min_value=0, max_value=123456789)
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        slug_field='id',
    )
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_ingredients(self, value):
        lst = []
        for ingredient in value:
            i = ingredient['id'].pk
            lst.append(i)
        lst_2 = list(set(lst))
        if len(lst_2) != len(lst):
            raise serializers.ValidationError('Ингредиенты дублируются.')
        else:
            return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            name=validated_data['name'],
            image=validated_data['image'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time'],
        )
        lst_tags = list(set(tags))
        for tag in lst_tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)

        for ingredient in ingredients:
            amount = ingredient['amount']
            data = {
                'recipe': recipe.pk,
                'ingredient': ingredient['id'].pk,
                'amount': amount
            }
            serializer = RecipeIngredientSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.image = validated_data.get('image', instance.image)

        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            lst_tags = list(set(tags))
            tags_old = instance.tags.all()
            for tag in tags_old:
                RecipeTag.objects.filter(
                        recipe=instance.pk,
                        tag=tag.pk
                    ).delete()
            lst_tags_2 = []
            for tag in lst_tags:
                current_tag = get_object_or_404(Tag, pk=tag.pk)
                RecipeTag.objects.create(
                    recipe=get_object_or_404(Recipe, pk=instance.pk),
                    tag=current_tag)
                id = current_tag.pk
                lst_tags_2.append(id)
            instance.tags.set(lst_tags_2)

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            ingredients_old = instance.ingredients.all()
            for ingredient in ingredients_old:
                RecipeIngredient.objects.filter(
                    recipe=instance.pk,
                    ingredient=ingredient.pk
                ).delete()
            lst_ingredients = []
            for ingredient in ingredients:
                current_amount = ingredient['amount']
                current_ingredient = get_object_or_404(
                    Ingredient, pk=ingredient['id'].pk
                )
                RecipeIngredient.objects.create(
                    recipe=get_object_or_404(Recipe, pk=instance.pk),
                    ingredient=current_ingredient,
                    amount=current_amount)
                lst_ingredients.append(current_ingredient)
            instance.ingredients.set(lst_ingredients)

        instance.save()
        return instance

    def to_representation(self, obj):
        data = RecipeReadOnlySerializer(
            obj, context={'request': self.context.get('request')}).data
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            ingredient['amount'] = (
                    RecipeIngredient.objects.get(
                        recipe=data['id'], ingredient=ingredient['id']
                        ).amount
                 )
        return data


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    # image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart', )

    def to_representation(self, obj):
        data = super(RecipeReadOnlySerializer, self).to_representation(obj)
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            id = ingredient['id']
            ingredient['amount'] = (
                RecipeIngredient.objects.get(
                    recipe=obj.pk, ingredient=id
                ).amount
            )
        return data

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.pk
        return Favorite.objects.filter(recipe=obj.pk, user=user_id).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.pk
        return ShoppingCart.objects.filter(
            recipe=obj.pk, user=user_id
        ).exists()


class ResponseShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time', )
        model = Recipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='id',
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', )

    def to_representation(self, obj):
        return ResponseShoppingCartSerializer(obj.recipe).data
