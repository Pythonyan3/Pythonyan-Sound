from rest_framework.serializers import ModelSerializer

from playlists.models import Playlist


class PlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("songs", )


class ShortPlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", )
        ordering = ("title", )


class SearchPlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", "cover")
