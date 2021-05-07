from rest_framework.fields import BooleanField
from rest_framework.serializers import ModelSerializer

from music.models import Song
from profiles.serializers import UsernameProfileSerializer


class SongSerializer(ModelSerializer):
    artist = UsernameProfileSerializer()
    is_liked = BooleanField(default=True)

    class Meta:
        model = Song
        exclude = ("genre", "listens", )
        read_only_fields = ("id", "artist")


class SongCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ("artist", "listens",)
        read_only_fields = ("id", )
