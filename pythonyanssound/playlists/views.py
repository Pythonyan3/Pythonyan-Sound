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
from playlists.serializers import PlaylistDetailsSerializer, ShortListPlaylistsSerializer, PlaylistCreateUpdateDeleteSerializer, \
    ListPlaylistsSerializer
from pythonyanssound.pagination import CustomPageNumberPagination


class PlaylistListCreateView(generics.ListCreateAPIView):
    """
    Allow access only authenticated users
    Processes GET method to retrieve list of authenticated user's playlists
    Processes POST method to create new user's playlist
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user).order_by("title")

    def create(self, request: Request, *args, **kwargs):
        serializer = PlaylistCreateUpdateDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PlaylistRetrieveUpdateDeleteView(APIView):
    """
    Processes GET method to retrieve playlist by playlist_id.
    Processes PUT method to update playlist with entered playlist_id.
    Processes DELETE method to delete playlist with entered playlist_id.
    Uses custom permission class to allow PUT/DELETE methods only for playlist owner
    """
    permission_classes = [IsAuthenticated, IsPlaylistOwner]
    serializer_class = PlaylistDetailsSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request: Request, playlist_id: int):
        """
        Returns requested playlist by playlists_id
        Allowed for all authenticated users
        """
        playlist = Playlist.objects.annotate(
            is_liked=Exists(self.request.user.liked_playlists.filter(pk=OuterRef("pk")))
        ).get(pk=playlist_id)
        serializer = self.serializer_class(instance=playlist, context=self.get_serializer_context())
        return Response(serializer.data)

    def put(self, request: Request, playlist_id: int):
        """
        Update playlist by requested playlist_id with requested data.
        Allowed only for authenticated user who's owner of playlist
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        serializer = PlaylistCreateUpdateDeleteSerializer(instance=playlist, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request: Request, playlist_id: int):
        """
        Delete playlist by requested playlist_id.
        Allowed only for authenticated user who's owner of playlist
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        serializer = PlaylistCreateUpdateDeleteSerializer(instance=playlist)
        playlist.delete()
        return Response(serializer.data)


class ShortPlaylistListView(ListAPIView):
    """
    Processes GET method to obtain list of authenticated user's playlists
    Returning data contains minimum information about playlists
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShortListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user.pk).order_by("title")


class SongAddRemovePlaylistView(APIView):
    """
    Processes POST method to add song with song_id to user's playlist with playlist_id
    Allowed only for authenticated user's and playlist's owners
    """
    permission_classes = [IsAuthenticated, IsPlaylistOwner]

    def post(self, request: Request, playlist_id: int, song_id: int):
        """
        Gets song and playlist by song_id and playlist_id
        Append song to playlist's songs (many to many relation)
        Also checks object level permission on playlist
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        song = Song.objects.get(pk=song_id)

        SongInPlaylist.objects.create(playlist=playlist, song=song)
        return Response(data={"message": f"{song}  successful added to {playlist}."})

    def delete(self, request: Request, playlist_id: int, song_id: int):
        """
        Gets song and playlist by song_id and playlist_id
        Remove song from playlist's songs (many to many relation)
        Also checks object level permission on playlist
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        song = Song.objects.get(pk=song_id)
        playlist.songs.remove(song)
        return Response(data={"message": f"{song}  successful removed from {playlist}."})


class LikedPlaylistsListView(ListAPIView):
    """
    LIST OF USER'S LIKED PLAYLISTS
    Processes GET method to obtain authenticated user's liked playlists
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return self.request.user.liked_playlists.order_by("title")


class LikeUnlikePlaylistView(APIView):
    """
    Processes POST method to add playlist to authenticated user's liked playlists list.
    Processes DELETE method to remove playlist from authenticated user's liked playlists list.
    Allowed only for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, playlist_id: int):
        """
        LIKE PLAYLIST
        Retrieves playlist by requested playlist_id
        Puts playlist to authenticated user's liked_playlists (many to many relation)
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        request.user.liked_playlists.add(playlist)
        return Response(data={"message": f"{playlist} playlist successful added to liked list."})

    def delete(self, request: Request, playlist_id: int):
        """
        UNLIKE PLAYLIST
        Retrieves playlist by requested playlist_id.
        Deletes playlist to authenticated user's liked_playlists (many to many relation)
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        request.user.liked_playlists.remove(playlist)
        return Response(data={"message": f"{playlist} playlist successful removed from liked list."})


class PlaylistsNewReleasesView(ListAPIView):
    pass
