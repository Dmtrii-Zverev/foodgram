from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import APIFollow, UsersMeView, UserViewSet


router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('subscriptions/', APIFollow.as_view()),
    path('<int:pk>/subscribe/', APIFollow.as_view()),
    path('me/avatar/', UsersMeView.as_view()),
    path('me/', UsersMeView.as_view()),
    path('', include(router.urls))
]
