from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewsSet
)


router = DefaultRouter()
router.register('recipes', RecipeViewsSet, basename='recipes')

v1_patterns = [
    path('', include(router.urls),)
]

urlpatterns = [
    path('v1/', include(v1_patterns)),
]
