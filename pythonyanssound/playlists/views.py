from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from playlists.models import Playlist
from playlists.permissions import IsPlaylistOwner
from playlists.serializers import PlaylistSerializer, ShortPlaylistSerializer


class PlaylistListCreateView(generics.ListCreateAPIView):
    """
    Allow access only authenticated users
    Processes GET method to retrieve list of authenticated user's playlists
    Processes POST method to create new user's playlist
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user)

    def create(self, request: Request, *args, **kwargs):
        request.data._mutable = True
        request.data['owner'] = request.user.pk
        request.data._mutable = False

        return super().create(request, *args, **kwargs)


class PlaylistRetrieveUpdateDeleteView(APIView):
    """
    Processes GET method to retrieve playlist by playlist_id.
    Processes PUT method to update playlist with entered playlist_id.
    Processes DELETE method to delete playlist with entered playlist_id.
    Uses custom permission class to allow PUT/DELETE methods only for playlist owner
    """
    permission_classes = [IsAuthenticated, IsPlaylistOwner]
    serializer_class = PlaylistSerializer

    def get(self, request: Request, playlist_id: int):
        """
        Returns requested playlist by playlists_id
        Allowed for all authenticated users
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        serializer = self.serializer_class(instance=playlist)
        return Response(serializer.data)

    def put(self, request: Request, playlist_id: int):
        """
        Update playlist by requested playlist_id with requested data.
        Allowed only for authenticated user who's owner of playlist
        """
        playlist = Playlist.objects.get(pk=playlist_id)
        self.check_object_permissions(request, playlist)
        serializer = self.serializer_class(instance=playlist, data=request.data, partial=True)
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
        serializer = self.serializer_class(instance=playlist)
        playlist.delete()
        return Response(serializer.data)


class ShortPlaylistListView(ListAPIView):
    """
    Processes GET method to obtain list of authenticated user's playlists
    Returning data contains minimum information about playlists
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShortPlaylistSerializer

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user.pk)


class LikesPlaylistsListView(ListAPIView):
    """
    LIST OF USER'S LIKED PLAYLISTS
    Processes GET method to obtain authenticated user's liked playlists
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        return self.request.user.liked_playlists


class LikePlaylistView(APIView):
    """
    Processes POST method to add playlist to authenticated user's liked playlists list.
    Processes DELETE method to remove playlist from authenticated user's liked playlists list.
    Allowed only for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, playlist_id: int):
        """
        LIKE PLAYLIST
        Retrieves playlist by requested playlist_id.
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
