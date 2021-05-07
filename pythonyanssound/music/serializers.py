from rest_framework.serializers import ModelSerializer

from music.models import Song


class SongSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ("listens", )
        read_only_fields = ("id", "artist")


class CreateSongSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ("artist", "listens", )
        read_only_fields = ("id", )


class ListSongSerializer(ModelSerializer):

    class Meta:
        model = Song
        fields = ['id', 'title', 'cover', 'audio']
