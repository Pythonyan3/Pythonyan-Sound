from django.db.models import Exists, OuterRef
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from music.serializers import SongSerializer
from playlists.models import Playlist
from profiles.serializers import UsernameProfileSerializer


class PlaylistDetailsSerializer(ModelSerializer):
    songs = SerializerMethodField("annotate_songs_with_likes")
    owner = UsernameProfileSerializer()

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "title", "cover", "owner", "songs")

    def annotate_songs_with_likes(self, instance: Playlist):
        profile = self.context.get("request").user
        songs = instance.songs.annotate(
            is_liked=Exists(profile.liked_songs.filter(pk=OuterRef("pk")))
        )
        serializer = SongSerializer(instance=songs, many=True)
        return serializer.data


class PlaylistCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "songs", "owner")


class ListPlaylistsSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", "cover")
        read_only_fields = ("id", "title", "cover")


class ShortListPlaylistsSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", )
        read_only_fields = ("id", "title")
