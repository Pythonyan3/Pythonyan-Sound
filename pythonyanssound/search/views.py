from django.db.models import Count, Exists, OuterRef
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.serializers import SongSerializer
from playlists.models import Playlist
from playlists.serializers import ListPlaylistsSerializer
from profiles.models import Profile
from profiles.serializers import ShortProfileSerializer
from pythonyanssound.pagination import CustomPageNumberPagination


class SearchListView(APIView):
    """Processes GET method to search songs, profiles and playlists."""
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request: Request, search_string: str):
        """
        Returns dict of Profiles, Playlists, Songs lists
        filtered by 'search_string'.

        Performs case insensitive filter by main fields of instances
        (song - title, playlist - title, profile - username)
        Also divides artist users and non artist users ordered by popularity
        (followers count)
        Lists len limited to 10 instances
        """
        # python's slices works like SQL LIMIT
        artists = Profile.objects.annotate(
            followers_count=Count("followers")
        ).filter(
            username__icontains=search_string, is_artist=True
        ).order_by('-followers_count')[:10]

        profiles = Profile.objects.annotate(
            followers_count=Count("followers")
        ).filter(
            username__icontains=search_string, is_artist=False
        ).order_by('-followers_count')[:10]

        playlists = Playlist.objects.filter(
            title__icontains=search_string
        )[:10]
        songs = Song.objects.annotate(
            is_liked=Exists(
                request.user.liked_songs.filter(pk=OuterRef("pk"))
            ),
        ).filter(title__icontains=search_string)[:10]

        artists_serializer = ShortProfileSerializer(
            instance=artists, many=True, context=self.get_serializer_context()
        )
        profile_serializer = ShortProfileSerializer(
            instance=profiles,
            many=True,
            context=self.get_serializer_context()
        )
        playlist_serializer = ListPlaylistsSerializer(
            instance=playlists,
            many=True,
            context=self.get_serializer_context()
        )
        song_serializer = SongSerializer(
            instance=songs, many=True, context=self.get_serializer_context()
        )
        return Response(data={
            "artists": artists_serializer.data,
            "profiles": profile_serializer.data,
            "playlists": playlist_serializer.data,
            "songs": song_serializer.data
        })


class ArtistsSearchView(ListAPIView):
    """Processes GET method to retrieve list of artists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ShortProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Profiles with 'is_artist' flag
        filtered by 'username' with 'search_string'.

        Orders artists by popularity (followers count descending)
        """
        return Profile.objects.annotate(
            followers_count=Count("followers")
        ).filter(
            username__icontains=self.kwargs.get("search_string"),
            is_artist=True
        ).order_by('-followers_count')


class ProfilesSearchView(ListAPIView):
    """Processes GET method to retrieve list of artists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ShortProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Profiles without 'is_artist' flag
        filtered by 'username' with 'search_string'.

        Orders artists by popularity (followers count descending)
        """
        return Profile.objects.annotate(
            followers_count=Count("followers")
        ).filter(
            username__icontains=self.kwargs.get("search_string"),
            is_artist=False
        ).order_by('-followers_count')


class PlaylistsSearchView(ListAPIView):
    """Processes GET method to retrieve list of playlists."""
    permission_classes = [IsAuthenticated]
    serializer_class = ListPlaylistsSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Playlists
        filtered by 'title' with 'search_string'.

        Orders playlists by 'title' ascending
        """
        return Playlist.objects.filter(
            title__icontains=self.kwargs.get("search_string")
        ).order_by("title")


class SongsSearchView(ListAPIView):
    """Processes GET method to retrieve list of songs."""
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of Songs
        filtered by 'title' with 'search_string'.

        Orders songs by 'title' ascending
        """
        return Song.objects.annotate(
            is_liked=Exists(
                self.request.user.liked_songs.filter(pk=OuterRef("pk"))
            ),
        ).filter(
            title__icontains=self.kwargs.get("search_string")
        ).order_by("title")
