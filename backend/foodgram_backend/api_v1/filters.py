import django_filters
from django.contrib.auth import get_user_model

from apps.recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(django_filters.FilterSet):
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset

        if value:
            return queryset.filter(in_carts__user=user)
        return queryset.exclude(in_carts__user=user)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset

        if value:
            return queryset.filter(in_favorits__user=user)
        return queryset.exclude(in_favorits__user=user)
