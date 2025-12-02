from rest_framework import filters, mixins, status, views, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from users.serializers import (
    UserSerializer,
    MeSerializer,
    AvatarSerializer
)
from api_v1.models import UserFollow, FavoriteRecipe


User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return MeSerializer
        if self.action == 'retrieve':
            return MeSerializer
        return UserSerializer
        


class UsersMeView(views.APIView):
    """Получение данных своей учетной записи.
        Доступно любому авторизованному пользователю.
        """

    def get(self, request):
        serializer = MeSerializer(request.user)
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
    

class FollowList(generics.ListCreateAPIView):
    permission_classes = ()
    serializer_class = UserSerializer
    queryset = User.objects.all()


class APIFollow(views.APIView):
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

