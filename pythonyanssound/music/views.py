from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.permissions import IsSongOwner
from music.serializers import SongSerializer, SongUpdateSerializer


class SongDetailsUpdateDeleteView(APIView):
    """
    Processes GET method to retrieve song by song_id.
    Processes PUT method to update song with entered song_id.
    Processes DELETE method to delete song with entered song_id.
    Uses custom permission class to allow PUT method only for song owner
    """

    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated, IsSongOwner]

    def get(self, request, song_id: int):
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.get(pk=song_id)
        serializer = self.serializer_class(instance=song)
        return Response(serializer.data)

    def put(self, request, song_id: int):
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = SongUpdateSerializer(data=request.data, instance=song, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)

    def delete(self, request, song_id: int):
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = self.serializer_class(instance=song)
        song.delete()
        return Response(serializer.data)


class SongsListCreateView(APIView):
    """
    Processes GET method to retrieve list of authenticated user's songs
    Processes POST method to create new user's song
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer

    def get(self, request):
        songs = Song.objects.filter(artist=request.user)
        serializer = SongSerializer(instance=songs, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        request.data['artist'] = request.user.pk
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
