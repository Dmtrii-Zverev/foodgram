from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api_v1.filters import RecipeFilter, IngredientFilter
from api_v1.pagination import CustomRecipePagination
from api_v1.permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from api_v1.serializers.recipes import (
    IngredientSerializer, ListRetrieveRecipeSerializer, ReadRecipeSerializer,
    RecipeSerializer, TagSerializer,
)
from apps.recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCartItem,
    Tag,
)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'options', 'head')
    pagination_class = CustomRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ListRetrieveRecipeSerializer
        if self.action == 'shopping_cart' or self.action == 'favorite_cart':
            return ReadRecipeSerializer
        return RecipeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all().prefetch_related('ingredients', 'tags')
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    user.shopping_cart.filter(recipe=OuterRef('pk'))
                ),
                is_favorited=Exists(
                    user.favorit_cart.filter(recipe=OuterRef('pk'))
                )
            )
        else:
            queryset = queryset.annotate(
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
                is_favorited=Value(False, output_field=BooleanField())
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        return self._get_read_response(instance, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self._get_read_response(instance, status.HTTP_200_OK)

    def _get_read_response(self, instance, status_code):
        instance = self.get_queryset().get(pk=instance.pk)
        serializer = ListRetrieveRecipeSerializer(
            instance,
            context={'request': self.request}
        )
        return Response(serializer.data, status=status_code)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        recipe = self.get_object()
        link = request.build_absolute_uri(recipe.short_url + '/')
        return Response({'short-link': link})

    @action(methods=['get'], detail=False, url_path='download_shopping_cart')
    def download_api_text(self, request, *args, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = [
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) — "
            f"{item['total_amount']}"
            for item in ingredients
        ]
        response_content = 'Список покупок:\n' + '\n'.join(content)
        response = HttpResponse(
            response_content,
            content_type='text/plain; charset=utf-8'
        )
        filename = 'ingredients.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        return self._manage_user_list(
            request, ShoppingCartItem, 'списке покупок'
        )

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite_cart(self, request, *args, **kwargs):
        return self._manage_user_list(request, FavoriteRecipe, 'избранном')

    def _manage_user_list(self, request, model, list_name):
        """Вспомогательный метод для управления корзиной/избранным."""
        user = request.user
        recipe = self.get_object()
        queryset = model.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if queryset.exists():
                return Response(
                    {'error': f'Рецепт уже в {list_name}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not queryset.exists():
            return Response(
                {'error': f'Рецепта нет в {list_name}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None
    queryset = Tag.objects.all()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def redirect_view(request, short_id):
    recipe = Recipe.objects.get(short_url='/s/' + short_id)
    serializer = ListRetrieveRecipeSerializer(
        recipe, context={'request': request}
    )
    return Response(serializer.data)
