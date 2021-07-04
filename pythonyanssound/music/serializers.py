from rest_framework.fields import BooleanField
from rest_framework.serializers import ModelSerializer

from music.models import Song
from profiles.models import Profile, SongLike


class SongArtistSerializer(ModelSerializer):
    """Redeclare serializer here to avoid circular import"""
    class Meta:
        model = Profile
        fields = ("id", "username")


class SongSerializer(ModelSerializer):
    artist = SongArtistSerializer()
    is_liked = BooleanField(default=False)

    class Meta:
        model = Song
        exclude = ("genre", "listens", "creation_date")
        read_only_fields = ("id", "artist")


class SongWithoutLikeSerializer(ModelSerializer):
    artist = SongArtistSerializer()

    class Meta:
        model = Song
        exclude = ("genre", "listens", "creation_date")
        read_only_fields = ("id", "artist")


class SongCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ("artist", "listens", "creation_date")
        read_only_fields = ("id", )


class SongLikeSerializer(ModelSerializer):
    song = SongWithoutLikeSerializer()
    is_liked = BooleanField(default=False)

    class Meta:
        model = SongLike
        fields = ("song", "like_date", "is_liked")
