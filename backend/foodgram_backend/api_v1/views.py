from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


from api_v1.models import (
    Recipe,
    Ingredient,
    Tag,
    ShoppingCartItem,
    RecipeIngredient,
    FavoriteRecipe
)
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    ReadRecipeSerializer,
    LinkRecipeSerializer,
    ListRetrieveRecipeSerializer
)

from .pagination import CustomRecipePagination
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from .filters import RecipeFilter

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'options', 'head')
    pagination_class = CustomRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'get_link':
            return LinkRecipeSerializer
        if self.action in ['list', 'retrieve']:
            return ListRetrieveRecipeSerializer
        if self.action == 'shopping_cart' or self.action == 'favorite_cart':
            return ReadRecipeSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'download_api_text':
            return (permissions.IsAuthenticated,)
        return super().get_permissions()

    def get_queryset(self):
        return Recipe.objects.all().prefetch_related('ingredients', 'tags')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        read_serializer = ListRetrieveRecipeSerializer(
            instance, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read_serializer = ListRetrieveRecipeSerializer(
            instance, context={'request': request})
        return Response(read_serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["get"], detail=True)
    def get_link(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = Recipe.objects.get(pk=recipe_id)
        serializer = self.get_serializer(recipe, context={'request': request})
        return Response(serializer.data)

    @action(["get"], detail=False, url_path='download_shopping_cart')
    def download_api_text(self, request):
        user = request.user
        data_from_db = ShoppingCartItem.objects.filter(
            user=user).values_list('recipe_id', flat=True)
        print(data_from_db)
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=data_from_db).select_related('ingredient')
        dict_ingredients = {}
        for obj in recipe_ingredients:
            if obj.ingredient.name not in dict_ingredients:
                dict_ingredients[obj.ingredient.name] = [
                    obj.ingredient.name, obj.ingredient.measurement_unit, obj.amount]
            else:
                new_amount = dict_ingredients[obj.ingredient.name][2] + obj.amount
                dict_ingredients[obj.ingredient.name] = [
                    obj.ingredient.name, obj.ingredient.measurement_unit, new_amount]
        lst = [
            f'{item[0]} ({item[1]}) - {item[2]}' for item in dict_ingredients.values()]
        response_content = '\n'.join(lst)
        print(response_content)
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        return response

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = ShoppingCartItem.objects.get_or_create(
                recipe=recipe, user=user)
            if not created:
                return Response(
                    {'error': 'Рецепт с таким названием уже добавлен с список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data)
        try:
            obj = ShoppingCartItem.objects.get(recipe=recipe, user=user)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCartItem.DoesNotExist:
            return Response(
                {'error': 'Рецепт с таким названием не добавлен с список покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = FavoriteRecipe.objects.get_or_create(
                recipe=recipe, user=user)
            if not created:
                return Response(
                    {'error': 'Рецепт с таким названием уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data)
        try:
            obj = FavoriteRecipe.objects.get(recipe=recipe, user=user)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт с таким названием не добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None
    queryset = Tag.objects.all()
