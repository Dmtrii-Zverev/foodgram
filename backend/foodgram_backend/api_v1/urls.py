from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    shopping_cart,
    download_api_text,
    favorite_cart
)


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_api_text),
    path('', include(router.urls)),
    #path('', include('djoser.urls')),
    path('users/', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/shopping_cart/', shopping_cart),
    path('recipes/<int:id>/favorite/', favorite_cart)
]
