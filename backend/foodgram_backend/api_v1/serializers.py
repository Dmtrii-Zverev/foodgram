import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import (
    UNIT_CHOICES,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.ChoiceField(choices=UNIT_CHOICES)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class WriteIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(
        required=True,
        min_value=1
    )

    def validate_id(self, value):
        try:
            Ingredient.objects.get(pk=value)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError('Ингдедиента нет в базе данных')
        return value


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = WriteIngredientSerializer(
        many=True, write_only=True, required=True, allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        write_only=True, allow_empty=False, required=True
    )
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'image', 'ingredients',
                  'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

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
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.add(*tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            RecipeIngredient.objects.filter(recipe=instance).delete()
            recipe_ingredients_list = []
            for item in ingredients:
                ingredient_id = item.get('id')
                amount = item.get('amount')
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                recipe_ingredients_list.append(
                    RecipeIngredient(
                        recipe=instance,
                        ingredient=ingredient,
                        amount=amount
                    )
                )
        RecipeIngredient.objects.bulk_create(recipe_ingredients_list)
        return super().update(instance, validated_data)


class ListRetrieveRecipeSerializer(serializers.ModelSerializer):
    from users.serializers import MeSerializer
    author = MeSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'image',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'text', 'cooking_time')

    def get_ingredients(self, obj):
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


class ReadRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()
