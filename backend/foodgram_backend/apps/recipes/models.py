from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from shortuuid.django_fields import ShortUUIDField

from .constants import (
    MAX_AMOUNT, MAX_COOKING_TIME, MAX_LENGTH_CHAR, MAX_LENGTH_TEXT, MIN_AMOUNT,
    MIN_COOKING_TIME,
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
        max_length=MAX_LENGTH_CHAR,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_CHAR,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_CHAR,
        choices=UNIT_CHOICES
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT, message='Кол-во не может быть меньше 1.'
            ),
            MaxValueValidator(
                MAX_AMOUNT, message='Кол-во не может быть больше 32000.'
            )
        ]
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'


class Recipe(models.Model):
    short_url = ShortUUIDField(
        length=5,
        max_length=10,
        prefix='/s/',
        alphabet='abcdefg12340',
        unique=True,
        editable=False,
        verbose_name='Короткий ID для ссылки'
    )
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
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME, message='Время не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME, message='Время не может превышать 1 суток.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['id']

    def __str__(self):
        return self.name


class ShoppingCartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ['id']
        verbose_name = 'Корзина рецептов'
        verbose_name_plural = 'Корзина рецептов'

    def __str__(self):
        return f'{self.user}, {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorit_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorits',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ['id']
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user}, {self.recipe}'
