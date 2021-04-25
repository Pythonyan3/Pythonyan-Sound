from rest_framework.serializers import ModelSerializer

from music.models import Song


class SongSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ['listens']


class SongUpdateSerializer(ModelSerializer):

    class Meta:
        model = Song
        exclude = ['id', 'artist', 'listens']
