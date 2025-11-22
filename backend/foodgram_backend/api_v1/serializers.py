import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from .models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient
)


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


class TagSerializer(serializers.Serializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        field = '__all__'


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
        fields = ('tags', 'image', 'ingredients',
                  'name', 'text', 'cooking_time', 'ingredients_details')
        
    def get_ingredients_details(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=obj
        ).select_related('ingredient')
        
        # Формируем список в нужном формате
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
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        recipe_ingredients_list = []
        print(ingredients)
        for item in ingredients:
            print(item)
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
    