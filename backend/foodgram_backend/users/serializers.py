from rest_framework import serializers
#from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from api_v1.serializers import Base64ImageField
from api_v1.models import UserFollow


User = get_user_model()


#class UserSerializer(UserCreateSerializer):
#    email = serializers.EmailField(required=True)
#    first_name = serializers.CharField(required=True, max_lenght=150)
#    last_name = serializers.CharField(required=True, max_lenght=150)
#    username = serializers.CharField(required=True, max_lenght=150)
#
#    class Meta:
#        model = User
#        fields = UserCreateSerializer.Meta.fields + ('email', 'first_name', 'last_name', 'username')


class MeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            is_sub = UserFollow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
            return is_sub
        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class ReadRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')
        
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_str = request.query_params.get('recipes_limit', 10)
        limit = int(limit_str)
        recipes = obj.recipes.all()[:limit]
        serializer = ReadRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        return True
