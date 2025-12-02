from django.db import models
from django.core.exceptions import ValidationError
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
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='recipes')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.PositiveSmallIntegerField('количество')

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
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


class UserRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'user')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'user')


class UserFollow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя.')
