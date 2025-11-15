from rest_framework import viewsets

from .models import (
    Recipe
)
from .serializers import(
    RecipeSerializer
)


class RecipeViewsets(viewsets.ModelViewSet):
    model = Recipe
    serializers_class = RecipeSerializer
    queryset = Recipe.objects.all()
