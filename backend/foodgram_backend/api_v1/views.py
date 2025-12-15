from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Value, BooleanField


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
                    ShoppingCartItem.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                ),
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
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
        # Получаем объект через get_queryset(), для доп полей.
        instance = self.get_queryset().get(pk=instance.pk)
        read_serializer = ListRetrieveRecipeSerializer(
            instance, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Получаем объект через get_queryset(), для доп полей.
        instance = self.get_queryset().get(pk=instance.pk)
        read_serializer = ListRetrieveRecipeSerializer(
            instance, context={'request': request})
        return Response(read_serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["get"], detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        recipe = self.get_object()
        link = request.build_absolute_uri(recipe.short_url + '/')
        return Response({'short-link': link})

    @action(["get"], detail=False, url_path='download_shopping_cart')
    def download_api_text(self, request, *args, **kwargs):
        user = request.user
        data_from_db = ShoppingCartItem.objects.filter(
            user=user).values_list('recipe_id', flat=True)
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
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        return response

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            obj, created = ShoppingCartItem.objects.get_or_create(
                recipe=recipe, user=user)
            if not created:
                return Response(
                    {'error': 'Рецепт с таким названием уже добавлен с список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    def favorite_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            obj, created = FavoriteRecipe.objects.get_or_create(
                recipe=recipe, user=user)
            if not created:
                return Response(
                    {'error': 'Рецепт с таким названием уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None
    queryset = Tag.objects.all()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def redirect_view(request, short_id):
    print(short_id)
    recipe = Recipe.objects.get(short_url='/s/'+short_id)
    serializer = ListRetrieveRecipeSerializer(recipe, context={'request': request})
    return Response(serializer.data)
