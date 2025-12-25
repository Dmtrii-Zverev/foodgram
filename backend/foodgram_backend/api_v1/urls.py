from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_v1.views.recipes import IngredientViewSet, RecipeViewSet, TagViewSet
from api_v1.views.users import UsersMeView, UserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='user')

users_patterns = [
    path('', UsersMeView.as_view()),
    path('avatar/', UsersMeView.as_view())
]

urlpatterns = [
    path('users/me/', include(users_patterns)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
