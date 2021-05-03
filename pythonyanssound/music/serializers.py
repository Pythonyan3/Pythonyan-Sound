from rest_framework.serializers import ModelSerializer

from music.models import Song


class SongSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ['listens']
        read_only_fields = ['artist']


class SearchSongSerializer(ModelSerializer):

    class Meta:
        model = Song
        fields = ['id', 'title', 'cover', 'audio']
