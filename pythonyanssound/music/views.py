from django.db.models import Exists, OuterRef
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.permissions import IsSongOwner, IsArtist
from music.serializers import SongSerializer, SongCreateUpdateDeleteSerializer
from music.services import get_paginated_songs_list_response
from pythonyanssound.pagination import CustomPageNumberPagination


class SongsListCreateView(APIView):
    """
    Allow access only authenticated artists users
    Processes GET method to retrieve list of authenticated user's songs
    Processes POST method to create new user's song
    """
    permission_classes = [IsAuthenticated, IsArtist]
    serializer_class = SongSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request: Request):
        """
        Returns authenticated user's own songs
        Uses custom pagination class
        """
        return get_paginated_songs_list_response(request, self)

    def post(self, request: Request):
        """
        Creates new song.
        Sets as song owner current authenticated user.
        """
        serializer = SongCreateUpdateDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # adding artist field programmatically to avoid creating song with other user as owner
        serializer.save(artist=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SongDetailsUpdateDeleteView(APIView):
    """
    Processes GET method to retrieve song by song_id.
    Processes PUT method to update song with entered song_id.
    Processes DELETE method to delete song with entered song_id.
    Uses custom permission class to allow PUT/DELETE method only for song owner
    """
    # IsSongOwner is object level permission has to be called before response
    permission_classes = [IsAuthenticated, IsSongOwner]
    serializer_class = SongSerializer

    def get(self, request: Request, song_id: int):
        """
        Returns requested song by song_id.
        Allowed to all authenticated users
        """
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.annotate(
            is_liked=Exists(request.user.liked_songs.filter(pk=OuterRef("pk")))
        ).get(pk=song_id)
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
        serializer = SongCreateUpdateDeleteSerializer(data=request.data, instance=song, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, song_id: int):
        """
        Deletes song by requested song_id.
        Allowed only for authenticated song's artist
        """
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = SongCreateUpdateDeleteSerializer(instance=song)
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
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return self.request.user.liked_songs.order_by("title")


class LikeSongView(APIView):
    """
    Processes POST method to add song to authenticated user's liked songs list.
    Processes DELETE method to remove song from authenticated user's liked songs list.
    Allowed only for authenticated users.
    """
    permission_classes = [IsAuthenticated]

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
        song = request.user.liked_songs.get(pk=song_id)
        request.user.liked_songs.remove(song)
        return Response(data={"message": f"{song} song successful removed from liked list."})
