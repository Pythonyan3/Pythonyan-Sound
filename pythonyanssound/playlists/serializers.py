from rest_framework.serializers import ModelSerializer

from playlists.models import Playlist


# TODO Add serializers with nested relationships

class PlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "songs", "owner")


class PlaylistsDetailsSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "title", "cover", "owner", "songs")


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
