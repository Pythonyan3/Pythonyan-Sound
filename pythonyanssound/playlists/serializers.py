from rest_framework.serializers import ModelSerializer

from playlists.models import Playlist


class PlaylistSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
