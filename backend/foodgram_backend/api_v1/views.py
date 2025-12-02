from rest_framework import viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


from api_v1.models import (
    Recipe,
    Ingredient,
    Tag,
    UserRecipe,
    RecipeIngredient,
    FavoriteRecipe,
    UserFollow
)
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    ReadRecipeSerializer,
    UserSerializer
)


User = get_user_model()


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
    permission_classes = ()
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = ()
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


@api_view(['POST', 'DELETE'])
def shopping_cart(request, id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        obj, created = UserRecipe.objects.get_or_create(
            recipe=recipe, user=user)
        if not created:
            return Response(
                {'error': 'Рецепт с таким названием уже добавлен с список покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ReadRecipeSerializer(recipe).data)
    try:
        obj = UserRecipe.objects.get(recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except UserRecipe.DoesNotExist:
        return Response(
            {'error': 'Рецепт с таким названием не добавлен с список покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def download_api_text(request):
    user = request.user
    data_from_db = UserRecipe.objects.filter(
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
    print(dict_ingredients)
    lst = [
        f'{item[0]} ({item[1]}) - {item[2]}' for item in dict_ingredients.values()]
    response_content = '\n'.join(lst)
    print(response_content)

    response = HttpResponse(response_content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
    return response


@api_view(['POST', 'DELETE'])
def favorite_cart(request, id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        obj, created = FavoriteRecipe.objects.get_or_create(
            recipe=recipe, user=user)
        if not created:
            return Response(
                {'error': 'Рецепт с таким названием уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ReadRecipeSerializer(recipe).data)
    try:
        obj = FavoriteRecipe.objects.get(recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except FavoriteRecipe.DoesNotExist:
        return Response(
            {'error': 'Рецепт с таким названием не добавлен в избранное.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowList(generics.ListCreateAPIView):
    permission_classes = ()
    serializer_class = UserSerializer
    queryset = User.objects.all()


class APIFollow(APIView):
    def get(self, request):
        user = request.user
        users = UserFollow.objects.filter(
            user=user).values_list('user', flat=True)
        print(users)
        followers = User.objects.filter(id__in=users)
        print(followers)
        return Response(UserSerializer(followers, many=True).data)

    def post(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if user == author:
            return Response(
                {'error': 'Вы не можете подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj, created = UserFollow.objects.get_or_create(
            user=user, author=author)
        if not created:
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(UserSerializer(author).data)

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        try:
            obj = UserFollow.objects.get(user=user, author=author)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт с таким названием не добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
