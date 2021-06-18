from django.contrib.auth.models import update_last_login
from django.db.models import Exists, OuterRef, Count
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, BooleanField
from rest_framework_simplejwt.serializers import TokenObtainSerializer, PasswordField
from rest_framework_simplejwt.settings import api_settings

from music.serializers import SongSerializer
from playlists.serializers import ListPlaylistsSerializer
from .models import Profile
from .tokens import CustomRefreshToken, VerifyToken


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profiles serializer, includes all Profile fields to show to user
    """
    class Meta:
        model = Profile
        fields = ('id', 'email', 'username', 'photo', 'biography', 'is_artist', 'is_verified')
        read_only_fields = ("id", "is_artist", "is_verified")


class ProfileDetailsSerializer(serializers.ModelSerializer):
    playlists = ListPlaylistsSerializer(many=True)
    songs = SerializerMethodField("annotate_and_limit_popular_songs")
    is_followed = BooleanField()

    class Meta:
        model = Profile
        fields = ('id', 'username', 'photo', 'biography', 'playlists', 'songs', 'is_followed', 'is_artist', 'is_verified')
        read_only_fields = ("id", "is_artist", "is_verified")

    def annotate_and_limit_popular_songs(self, profile: Profile):
        if profile.is_artist:
            authorized_profile = self.context.get("request").user
            songs = profile.songs.annotate(
                is_liked=Exists(authorized_profile.liked_songs.filter(pk=OuterRef("pk"))),
                likes_count=Count("liked_profiles")
            ).order_by("-likes_count")[:10]
            serializer = SongSerializer(songs, many=True, context=self.context)
            return serializer.data
        serializer = SongSerializer(many=True, context=self.context)
        return serializer.data


class ShortProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'photo', 'is_artist')


class ProfileCreateSerializer(serializers.ModelSerializer):
    """
    Profile registration serializer, takes only required fields.
    Also includes additional field - "confirm_password"
    """
    confirm_password = serializers.CharField(max_length=128)

    class Meta:
        model = Profile
        fields = ('email', 'username', 'password', 'confirm_password')
        extra_kwargs = {
            "username": {
                "error_messages": {
                    "blank": "Please enter your username"
                }
            },
            "email": {
                "error_messages": {
                    "blank": "Please enter your email address"
                }
            }
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError("Passwords must match", code=status.HTTP_400_BAD_REQUEST)
        return attrs


class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

    def validate(self, attrs):
        VerifyToken(attrs['token'])
        return attrs


class LoginSerializer(TokenObtainSerializer):
    """
    Custom token pair obtain serializer
    Creates new tokens pair for user
    """

    default_error_messages = {
        'no_active_account': ('Incorrect username or password', )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(error_messages={
            "blank": "Please enter your username or email address"
        })
        self.fields['password'] = PasswordField(error_messages={
            "blank": "Please enter your password"
        })

    @classmethod
    def get_token(cls, user):
        return CustomRefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["id"] = self.user.pk
        data["username"] = self.user.username
        data["photo"] = str(self.user.photo)
        data["is_artist"] = self.user.is_artist
        data["is_verified"] = self.user.is_verified
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
        if attrs.get("refresh"):
            return attrs


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


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    confirm_new_password = serializers.CharField(max_length=128)
