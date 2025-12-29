from django.contrib.auth import get_user_model
from rest_framework import serializers

from api_v1.constants import (
    MAX_AMOUNT, MAX_COOKING_TIME, MIN_AMOUNT, MIN_COOKING_TIME,
)
from api_v1.serializers.base import Base64ImageField
from apps.recipes.models import (
    UNIT_CHOICES, Ingredient, Recipe, RecipeIngredient, Tag,
)

User = get_user_model()


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
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value': 'Кол-во ингредиента не может быть меньше 1.',
            'max_value': 'Кол-во ингредиента не может быть больше 32000.'
        }
    )

    def validate_id(self, value):
        try:
            Ingredient.objects.get(pk=value)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError('Ингредиента нет в базе данных')
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
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        error_messages={
            'min_value': 'Время не может быть меньше 1 минуты',
            'max_value': 'Время не может превышать 1 суток.'
        }
    )

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

    def _set_ingredients(self, recipe, ingredients_data):
        recipe.recipes.all().delete()

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=item.get('id'),
                    amount=item.get('amount')
                ) for item in ingredients_data
            ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        self._set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.add(*tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            self._set_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class MeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            is_sub = obj.followers.all().exists()
            return is_sub
        return False


class ListRetrieveRecipeSerializer(serializers.ModelSerializer):
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
        recipe_ingredients = obj.recipes.all().select_related('ingredient')
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
