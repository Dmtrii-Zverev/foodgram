from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersMeView, UserViewSet

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('me/avatar/', UsersMeView.as_view()),
    path('me/', UsersMeView.as_view()),
    path('', include(router.urls))
]
