from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet
)


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
#router.register('tags')

v1_patterns = [
    path('', include(router.urls),)
]

urlpatterns = [
    path('v1/', include(v1_patterns)),
]
