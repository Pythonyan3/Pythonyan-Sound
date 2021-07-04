from django.db.models import Exists, OuterRef
from rest_framework.fields import SerializerMethodField, BooleanField
from rest_framework.serializers import ModelSerializer

from music.serializers import SongSerializer, SongWithoutLikeSerializer
from playlists.models import Playlist, SongInPlaylist
from profiles.models import Profile


class PlaylistOwnerSerializer(ModelSerializer):
    """Declare serializer here to avoid circular import"""
    class Meta:
        model = Profile
        fields = ("id", "username")


class SongInPlaylistSerializer(ModelSerializer):
    song = SongWithoutLikeSerializer()
    is_liked = BooleanField(default=False)

    class Meta:
        model = SongInPlaylist
        fields = ("id", "song", "adding_date", "is_liked")


class PlaylistDetailsSerializer(ModelSerializer):
    songs = SerializerMethodField("annotate_songs_with_likes")
    owner = PlaylistOwnerSerializer()
    is_liked = BooleanField(default=False)

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "title", "cover", "owner", "songs", "creation_date")

    def annotate_songs_with_likes(self, instance: Playlist):
        profile = self.context.get("request").user
        # use m2m through model to order by adding date
        songs = instance.songs_through.annotate(
            is_liked=Exists(profile.liked_songs.filter(pk=OuterRef("song__pk")))
        )
        serializer = SongInPlaylistSerializer(instance=songs, many=True, context=self.context)
        return serializer.data


class PlaylistCreateUpdateDeleteSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = "__all__"
        read_only_fields = ("id", "songs", "owner", "creation_date")


class ListPlaylistsSerializer(ModelSerializer):

    owner = PlaylistOwnerSerializer()

    class Meta:
        model = Playlist
        fields = ("id", "title", "owner", "cover")
        read_only_fields = ("id", "title", "owner", "cover", "creation_date")


class ShortListPlaylistsSerializer(ModelSerializer):

    class Meta:
        model = Playlist
        fields = ("id", "title", )
        read_only_fields = ("id", "title")
