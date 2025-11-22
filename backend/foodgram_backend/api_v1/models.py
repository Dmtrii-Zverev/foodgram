from django.db import models
from django.contrib.auth import get_user_model

from .constants import (
    MAX_LENGTH_CHAR,
    MAX_LENGTH_TEXT
)

UNIT_CHOICES = (
    ('г', 'грамм'),
    ('кг', 'килограмм'),
    ('шт.', 'штук'),
    ('мл', 'миллилитры'),
    ('по вкусу', 'по вкусу'),
    ('ст. л.', 'столовая ложка'),
    ('ч. л.', 'чайная ложка'),
    ('щепотка', 'щепотка'),
    ('капля', 'капля',)

)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR, unique=True, verbose_name='Название'
    )
    slug = models.SlugField(max_length=MAX_LENGTH_CHAR, unique=True)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR, unique=True, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_LENGTH_CHAR, choices=UNIT_CHOICES
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='recipes')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.PositiveSmallIntegerField('количество')

    def __str__(self):
        return self.recipe, self.ingredient, self.amount

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR, verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='api_v1/images/',
        null=True,
        default=None
    )
    text = models.TextField('Текст', max_length=MAX_LENGTH_TEXT)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах'
        # Добавитиь валидаторы на мин и макс значения.
    )
