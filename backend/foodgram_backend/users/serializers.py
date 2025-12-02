from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from api_v1.serializers import Base64ImageField
from api_v1.models import UserFollow


User = get_user_model()


class UserSerializer(UserCreateSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = UserCreateSerializer.Meta.fields + ('email', 'first_name', 'last_name')


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        is_sub = UserFollow.objects.filter(
            user=request.user,
            author=obj
        ).exists()
        return is_sub


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
