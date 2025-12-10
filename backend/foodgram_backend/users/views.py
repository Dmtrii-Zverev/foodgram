from rest_framework import filters, mixins, status, views, viewsets, permissions
from djoser.serializers import SetPasswordSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from users.serializers import (
    UserSerializer,
    MeSerializer,
    AvatarSerializer,
    FollowSerializer
)
from api_v1.models import UserFollow
from api_v1.pagination import CustomRecipePagination
from api_v1.permissions import IsAdminOrAuthorOrReadOnly


User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    queryset = User.objects.all()
    pagination_class = CustomRecipePagination

    def get_serializer_class(self):
        if self.action == 'list':
            return MeSerializer
        elif self.action == 'retrieve':
            return MeSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscriptions':
            return FollowSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return (permissions.AllowAny(),)
        elif self.action == 'subscriptions':
            return (permissions.IsAuthenticated,)
        return super().get_permissions()
    
    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        users = UserFollow.objects.filter(
            user=request.user).values_list('user', flat=True)
        followers = User.objects.filter(id__in=users)
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followers, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = self.get_object()
        if user == author:
            return Response(
                {'error': 'Вы не можете быть подписанным на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            obj, created = UserFollow.objects.get_or_create(
                user=user, author=author)
            if not created:
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(FollowSerializer(author).data)
        try:
            obj = UserFollow.objects.get(user=user, author=author)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserFollow.DoesNotExist:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UsersMeView(views.APIView):
    """Получение данных своей учетной записи.
        Доступно любому авторизованному пользователю.
        """
    def get(self, request):
        serializer = MeSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
