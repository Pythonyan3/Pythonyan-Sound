from abc import ABCMeta

from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework_simplejwt.settings import api_settings

from .models import Profile
from .tokens import CustomRefreshToken


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'email', 'username', 'photo', 'biography', 'is_artist', 'is_verified']


class ProfileCreateSerializer(serializers.ModelSerializer):
    confirm_password = CharField(max_length=128)

    class Meta:
        model = Profile
        fields = ['email', 'username', 'password', 'confirm_password']

    def save(self, **kwargs):
        profile = Profile(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )

        if self.validated_data['password'] != self.validated_data['confirm_password']:
            raise serializers.ValidationError({'password': ["Passwords must match."]})

        profile.set_password(self.validated_data['password'])
        profile.save()
        return profile


class TokenRefreshSerializer(serializers.Serializer):
    """
    Custom serializer uses custom refresh token class
    """
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = CustomRefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = CustomRefreshToken(attrs['refresh'])
        return refresh
