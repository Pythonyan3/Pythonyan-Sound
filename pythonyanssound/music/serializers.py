from rest_framework.fields import BooleanField
from rest_framework.serializers import ModelSerializer

from music.models import Song
from profiles.models import Profile


class SongArtistSerializer(ModelSerializer):
    """Redeclare serializer here to avoid circular import"""
    class Meta:
        model = Profile
        fields = ("id", "username")


class SongSerializer(ModelSerializer):
    artist = SongArtistSerializer()
    is_liked = BooleanField(default=True)

    class Meta:
        model = Song
        exclude = ("genre", "listens", "upload_date")
        read_only_fields = ("id", "artist")


class SongCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ("artist", "listens", "upload_date")
        read_only_fields = ("id", )
