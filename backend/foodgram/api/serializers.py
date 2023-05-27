import webcolors
import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers
from users.models import User
from rest_framework.validators import UniqueTogetherValidator
# from djoser.serializers import UserSerializer as US
# from djoser.views import TokenCreateView
# from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer


from recipes.models import (
    Ingredient, Recipe, Tag, Favorite, ShopingCart,
    RecipeIngredient, RecipeTag
)
from users.models import (
    Follow
)


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


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id',
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        read_only_fields = ('user', )

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return data 


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset = User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        queryset = Recipe.objects.all(),
        slug_field='id',
    )
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', )

    # validators = [
    #     UniqueTogetherValidator(
    #         queryset=Favorite.objects.all(),
    #         fields = ('user', 'recipe'),
    #         message='Поля должны быть уникальными'
    #     )
    # ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

# delete
class RecipeIngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RecipeIngredient
        fields = ['recipe', 'ingredient', 'amount']


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeTag
        fields = ['recipe', 'tag']

# ХЗ НУЖОН ЛИ
class IngredientAmountSerializer(serializers.Serializer):

    amount = serializers.IntegerField(min_value=0, max_value=123456789)
    id = serializers.PrimaryKeyRelatedField(queryset=RecipeIngredient.objects.all())


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
    # ingredients = IngredientSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True)
    # ingredients = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all(),
    #     many=True,
    #     # slug_field='id',
    # )
    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def create(self, validated_data):
        print(validated_data)
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                    name=validated_data['name'],
                                    # image=validated_data['image'],
                                    text=validated_data['text'],
                                    cooking_time=validated_data['cooking_time'],
                                    )

        tags = validated_data.pop('tags')
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)

        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        for i in ingredients:
            # print(i)
            current_amount = i['amount']
            obj = i['id']
            # print(obj)
            current_ingredient = get_object_or_404(Ingredient, pk=obj.pk)
            # print(current_ingredient)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=current_amount,
            )
        return recipe
    
    def update(self, instance, validated_data):

        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        # instance.image = validated_data.get('image')
       
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            tags_old = instance.tags.all()
            # print(tags_old)
            for tag in tags_old:
                RecipeTag.objects.filter(
                        recipe=instance.pk,
                        tag=tag.pk
                    ).delete()
            lst_tags = []
            for tag in tags:
                current_tag = get_object_or_404(Tag, pk=tag.pk)
                new_tag = RecipeTag.objects.create(
                    recipe=get_object_or_404(Recipe, pk=instance.pk),
                    tag=current_tag)
                lst_tags.append(new_tag)
            # print(lst)
            
            instance.tags.set(lst_tags)
            
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            print(ingredients)
            ingredients_old = instance.ingredients.all()
            for ingredient in ingredients_old:
                RecipeIngredient.objects.filter(
                    recipe=instance.pk,
                    ingredient=ingredient.pk
                )
            lst_ingredients = []
            for ingredient in ingredients:
                current_amount = ingredient['amount']
                current_ingredient = get_object_or_404(Ingredient, pk=ingredient.pk)
                new_ingredient = RecipeIngredient.objects.create(
                    recipe=get_object_or_404(Recipe, pk=instance.pk),
                    ingredient=current_ingredient,
                    amount=current_amount)
                lst_ingredients.append(new_ingredient)

            instance.ingredients.set(lst_ingredients)
                
        instance.save()
        return instance



class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    # ingredients = serializers.SerializerMethodField('get_ingredients')
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')

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
        return ShopingCart.objects.filter(recipe=obj.pk, user=user_id).exists()


class ShopingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset = User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        queryset = Recipe.objects.all(),
        slug_field='id',
    )

    class Meta:
        model = ShopingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', )



# class UserListSerializer(serializers.ModelSerializer):
# 
#     class Meta:
#         model = User
#         fields = ('email', 'username', 'first_name', 'last_name', 'password', 'id' )
