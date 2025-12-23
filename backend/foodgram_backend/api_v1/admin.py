from django.contrib import admin
from django.db.models import Count

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCartItem, Tag, UserFollow)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    inlines = (IngredientInline,)
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            favorites_count=Count('in_favorits')
        )

    @admin.display(description='кол-во добавлений в избранное')
    def favorite_count(self, obj):
        return obj.favorites_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(UserFollow)
admin.site.register(ShoppingCartItem)
admin.site.register(FavoriteRecipe)
