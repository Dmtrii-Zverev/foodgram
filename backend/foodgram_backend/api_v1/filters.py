import django_filters
from .models import Recipe, Tag, ShoppingCartItem, FavoriteRecipe
from django.contrib.auth import get_user_model

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
        if self.request.user.is_authenticated and value:
            user_items = ShoppingCartItem.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=user_items)
            
        elif self.request.user.is_authenticated and not value:
            user_items = ShoppingCartItem.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
            return queryset.exclude(id__in=user_items)
        return queryset
    
    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            user_items = FavoriteRecipe.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=user_items)
        elif self.request.user.is_authenticated and not value:
            user_items = FavoriteRecipe.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
            return queryset.exclude(id__in=user_items)
        return queryset
