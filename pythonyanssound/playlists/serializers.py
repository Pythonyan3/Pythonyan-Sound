from rest_framework.serializers import ModelSerializer

from playlists.models import Playlist


class PlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"


class ShortPlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ('id', 'title', )
        ordering = ('title', )
