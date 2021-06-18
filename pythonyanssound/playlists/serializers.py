from django.db.models import Exists, OuterRef
from rest_framework.fields import SerializerMethodField, BooleanField
from rest_framework.serializers import ModelSerializer

from music.serializers import SongSerializer
from playlists.models import Playlist
from profiles.models import Profile


class PlaylistOwnerSerializer(ModelSerializer):
    """Redeclare serializer here to avoid circular import"""
    class Meta:
        model = Profile
        fields = ("id", "username")


class PlaylistDetailsSerializer(ModelSerializer):
    songs = SerializerMethodField("annotate_songs_with_likes")
    owner = PlaylistOwnerSerializer()
    is_liked = BooleanField()

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "title", "cover", "owner", "songs", "upload_date")

    def annotate_songs_with_likes(self, instance: Playlist):
        profile = self.context.get("request").user
        songs = instance.songs.annotate(
            is_liked=Exists(profile.liked_songs.filter(pk=OuterRef("pk")))
        )
        serializer = SongSerializer(instance=songs, many=True, context=self.context)
        return serializer.data


class PlaylistCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "songs", "owner", "upload_date")


class ListPlaylistsSerializer(ModelSerializer):

    owner = PlaylistOwnerSerializer()

    class Meta:
        model = Playlist
        fields = ("id", "title", "owner", "cover")
        read_only_fields = ("id", "title", "owner", "cover", "upload_date")


class ShortListPlaylistsSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", )
        read_only_fields = ("id", "title")
