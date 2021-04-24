from rest_framework import serializers

from music.models import Song


class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        exclude = ['listens']


class SongUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        exclude = ['id', 'artist', 'listens']
