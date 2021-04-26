from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.permissions import IsSongOwner, IsArtist
from music.serializers import SongSerializer, SongUpdateSerializer


class SongsListCreateView(APIView):
    """
    Allow access only authenticated artists users
    Processes GET method to retrieve list of authenticated user's songs
    Processes POST method to create new user's song
    """
    permission_classes = [IsAuthenticated, IsArtist]
    serializer_class = SongSerializer

    def get(self, request: Request):
        """
        Returns authenticated user's own songs
        """
        songs = Song.objects.filter(artist=request.user)
        serializer = SongSerializer(instance=songs, many=True)
        return Response(data=serializer.data)

    def post(self, request: Request):
        """
        Creates new song.
        Sets as song owner current authenticated user.
        """
        request.data._mutable = True
        request.data['artist'] = request.user.pk
        request.data._mutable = False

        serializer = SongSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class SongDetailsUpdateDeleteView(APIView):
    """
    Processes GET method to retrieve song by song_id.
    Processes PUT method to update song with entered song_id.
    Processes DELETE method to delete song with entered song_id.
    Uses custom permission class to allow PUT/DELETE method only for song owner
    """

    serializer_class = SongSerializer
    # IsSongOwner is object level permission has to be called before response
    permission_classes = [IsAuthenticated, IsSongOwner]

    def get(self, request: Request, song_id: int):
        """
        Returns requested song by song_id.
        Allowed to all authenticated users
        """
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.get(pk=song_id)
        serializer = self.serializer_class(instance=song)
        return Response(serializer.data)

    def put(self, request: Request, song_id: int):
        """
        Updates song by requested song_id with requested data.
        Allowed only for authenticated song's artist
        """
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = SongUpdateSerializer(data=request.data, instance=song, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, song_id: int):
        """
        Deletes song by requested song_id.
        Allowed only for authenticated song's artist
        """
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = self.serializer_class(instance=song)
        song.delete()
        return Response(serializer.data)


class LikedSongsListView(ListAPIView):
    """
    LIST OF LIKED SONGS
    Processes GET method to obtain list of liked songs of user
    Allowed only for authenticated users
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer

    def get_queryset(self):
        return self.request.user.liked_songs


class LikeSongView(APIView):
    """
    Processes POST method to add song to authenticated user's liked songs list.
    Processes DELETE method to remove song from authenticated user's liked songs list.
    Allowed only for authenticated users.
    """

    def post(self, request: Request, song_id: int):
        """
        LIKE SONG
        Retrieves song by requested song_id.
        Puts song to authenticated user's liked_songs (many to many relation)
        """
        song = Song.objects.get(pk=song_id)
        request.user.liked_songs.add(song)
        return Response(data={"message": f"{song} song successful added to liked list."})

    def delete(self, request: Request, song_id: int):
        """
        UNLIKE SONG
        Retrieves song by requested song_id.
        Deletes song to authenticated user's liked_songs (many to many relation)
        """
        song = Song.objects.get(pk=song_id)
        request.user.liked_songs.remove(song)
        return Response(data={"message": f"{song} song successful removed from liked list."})
