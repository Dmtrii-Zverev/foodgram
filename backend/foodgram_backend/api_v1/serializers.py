import base64

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from .models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    UserFollow
)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsSerializer(many=True, write_only=True)
    ingredients_details = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'image', 'ingredients',
                  'name', 'text', 'cooking_time', 'ingredients_details')
        
    def get_ingredients_details(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=obj
        ).select_related('ingredient')
        return [
            {
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'measurement_unit': ri.ingredient.measurement_unit,
                'amount': ri.amount
            }
            for ri in recipe_ingredients
        ]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        recipe_ingredients_list = []
        for item in ingredients:
            ingredient_id = item.get('id')
            amount = item.get('amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            recipe_ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        
        RecipeIngredient.objects.bulk_create(recipe_ingredients_list)
        print(recipe)
        return recipe


class ReadRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    recipes = ReadRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        return True
