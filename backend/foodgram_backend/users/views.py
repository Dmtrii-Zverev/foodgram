from api_v1.models import UserFollow
from api_v1.pagination import CustomRecipePagination
from api_v1.permissions import IsAdminOrAuthUserOrReadonly
from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers import AvatarSerializer, FollowSerializer, MeSerializer

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrAuthUserOrReadonly,)
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
        elif self.action == 'subscribe':
            return FollowSerializer
        return UserCreateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if self.action == 'subscribe' or self.action == 'subscriptions':
            queryset = queryset.annotate(
                recipes_count=Count('recipes')
            )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(UserFollow.objects.filter(
                    user=user, author=OuterRef('pk')
                ))
            )
        else:
            queryset = queryset.annotate(
                is_subscribed=Value(False, output_field=BooleanField())
            )
        return queryset

    @action(methods=['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        followers = self.get_queryset().filter(following__user=request.user)
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            followers, many=True, context={'request': request}
        )
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
        queryset = UserFollow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if queryset.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            UserFollow.objects.create(user=user, author=author)
            serializer = self.get_serializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UsersMeView(views.APIView):
    '''Получение данных своей учетной записи.
        Доступно любому авторизованному пользователю.
        '''
    def get(self, request):
        serializer = MeSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        if 'avatar' not in request.data:
            return Response(
                {'avatar': 'Это поле обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AvatarSerializer(
            request.user,
            data=request.data
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
