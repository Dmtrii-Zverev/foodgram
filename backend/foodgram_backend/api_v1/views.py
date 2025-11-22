from rest_framework import viewsets

from .models import (
    Recipe,
    Ingredient,
    Tag
)
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = ()
    http_method_names = ('get', 'post', 'patch', 'delete', 'options', 'head')
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = TitleFilter

    def get_queryset(self):
        return Recipe.objects.all().prefetch_related('ingredients', 'tags')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
