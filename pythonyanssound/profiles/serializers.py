from django.contrib.auth.models import update_last_login
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

from .models import Profile
from .tokens import CustomRefreshToken


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profiles serializer, includes all Profile fields to show to user
    """
    class Meta:
        model = Profile
        fields = ['id', 'email', 'username', 'photo', 'biography', 'is_artist', 'is_verified']


class SearchProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'photo']


class ProfileCreateSerializer(serializers.ModelSerializer):
    """
    Profile registration serializer, takes only required fields.
    Also includes additional field - "confirm_password"
    """
    confirm_password = serializers.CharField(max_length=128)

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


class LoginSerializer(TokenObtainSerializer):
    """
    Custom token pair obtain serializer
    Creates new tokens pair for user
    """

    @classmethod
    def get_token(cls, user):
        return CustomRefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class LogoutSerializer(serializers.Serializer):
    """
    Takes user's refresh token, throw exception if token is invalid or expired
    """
    refresh = serializers.CharField(max_length=255)

    def validate(self, attrs):
        return CustomRefreshToken(attrs['refresh'])


class TokenRefreshSerializer(serializers.Serializer):
    """
    Custom serializer uses custom refresh token class
    Creates new access token or both new refresh and access tokens
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


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    confirm_new_password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise ValidationError(
                detail={"detail": ["Incorrect profile's password!"]},
                code=status.HTTP_400_BAD_REQUEST
            )
        else:
            if validated_data['new_password'] == validated_data['confirm_new_password']:
                instance.set_password(validated_data['new_password'])
                instance.save()
                return instance
            else:
                raise ValidationError(
                    detail={"detail": ["New passwords must match!"]},
                    code=status.HTTP_400_BAD_REQUEST
                )
