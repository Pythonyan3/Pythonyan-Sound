from django.db.models import Exists, OuterRef
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from playlists.models import Playlist, SongInPlaylist
from playlists.permissions import IsPlaylistOwner
from playlists.serializers import (
    PlaylistDetailsSerializer, ShortListPlaylistsSerializer,
    PlaylistCreateUpdateDeleteSerializer, ListPlaylistsSerializer
)
from pythonyanssound.pagination import CustomPageNumberPagination


class PlaylistListCreateView(generics.ListCreateAPIView):
    """Processes GET/POST methods to create/retrieve playlists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Playlists owned by user who requests
        and ordered by title ascending.
        """
        return Playlist.objects.filter(
            owner=self.request.user
        ).order_by("title")

    def create(self, request: Request, *args, **kwargs):
        """
        Implementation of creating new Playlist.

        Sets Playlist's owner to user's Profile from request
        """
        serializer = PlaylistCreateUpdateDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class PlaylistRetrieveUpdateDeleteView(APIView):
    """
    Processes GET/PUT/DELETE methods to retrieve/update/delete playlist.

    Uses custom permission class
    to allow PUT/DELETE methods only for playlist owner
    """
    permission_classes = [IsAuthenticated, IsPlaylistOwner]
    serializer_class = PlaylistDetailsSerializer

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request: Request, playlist_id: int):
        """
        Returns playlist identified with 'playlist_id'
        passed as URL parameter.
        """
        playlist = Playlist.objects.annotate(
            is_liked=Exists(
                self.request.user.liked_playlists.filter(pk=OuterRef("pk"))
            )
        ).get(pk=playlist_id)
        serializer = self.serializer_class(
            instance=playlist, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request: Request, playlist_id: int):
        """
        Updates playlist identified with 'playlist_id'
        passed as URL parameter.
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        serializer = PlaylistCreateUpdateDeleteSerializer(
            instance=playlist, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request: Request, playlist_id: int):
        """
        Deletes playlist identified with 'playlist_id'
        passed as URL parameter.
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        serializer = PlaylistCreateUpdateDeleteSerializer(instance=playlist)
        playlist.delete()
        return Response(serializer.data)


class ShortPlaylistListView(ListAPIView):
    """Processes GET method to retrieve playlists with minimum info."""
    permission_classes = [IsAuthenticated]
    serializer_class = ShortListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Playlists owned by user who requests
        and ordered by title ascending.
        """
        return Playlist.objects.filter(
            owner=self.request.user.pk
        ).order_by("title")


class SongAddRemovePlaylistView(APIView):
    """Processes POST method to add song with song_id to user's playlist with playlist_id
    Allowed only for authenticated user's and playlist's owners
    """
    permission_classes = [IsAuthenticated, IsPlaylistOwner]

    def post(self, request: Request, playlist_id: int, song_id: int):
        """
        Appends Song with 'song_id' to Playlist with 'playlist_id'
        by creating SongInPlaylist instance (separate model).
        """
        # TODO replace creating instance with playlist and song instances
        #  with playlist and song ids
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        song = Song.objects.get(pk=song_id)

        SongInPlaylist.objects.create(playlist=playlist, song=song)
        return Response(
            data={"message": f"{song}  successful added to {playlist}."}
        )

    def delete(self, request: Request, playlist_id: int, song_id: int):
        """
        Delete Song with 'song_id' from Playlist with 'playlist_id'
        by removing SongInInstance.
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        song = Song.objects.get(pk=song_id)
        playlist.songs.remove(song)
        return Response(
            data={"message": f"{song}  successful removed from {playlist}."}
        )


class LikedPlaylistsListView(ListAPIView):
    """Processes GET method to obtain user's liked playlists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns list of user's liked playlists
        ordered by title ascending.
        """
        return self.request.user.liked_playlists.order_by("title")


class LikeUnlikePlaylistView(APIView):
    """
    Processes POST/DELETE methods to append/remove playlist
    to list of user's liked playlists.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, playlist_id: int):
        """
        Appends playlist with 'playlist_id' identifier
        to user's liked playlists.
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        request.user.liked_playlists.add(playlist)
        return Response(
            data={
                "message": f"{playlist} playlist "
                           f"successful added to liked list."
            }
        )

    def delete(self, request: Request, playlist_id: int):
        """
        Removes playlist with 'playlist_id' identifier
        from user's liked playlists.
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        request.user.liked_playlists.remove(playlist)
        return Response(
            data={
                "message": f"{playlist} playlist "
                           f"successful removed from liked list."
            }
        )


class PlaylistsNewReleasesView(ListAPIView):
    pass
