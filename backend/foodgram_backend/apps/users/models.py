# users/models.py
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .constants import (
    MAX_LENGTH_EMAIL, MAX_LENGTH_FIRST_NAME, MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_USERNAME,
)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[AbstractUser.username_validator],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class UserFollow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user}, {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя.')
