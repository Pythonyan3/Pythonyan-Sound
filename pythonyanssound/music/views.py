from datetime import timedelta

from django.db.models import Exists, OuterRef, BooleanField, Case
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.permissions import IsSongOwner, IsArtist
from music.serializers import (
    SongSerializer, SongCreateUpdateDeleteSerializer, SongLikeSerializer
)
from music.services import get_paginated_songs_list_response
from profiles.models import SongLike
from pythonyanssound.pagination import CustomPageNumberPagination


class SongsListCreateView(APIView):
    """Processes GET/POST method to retrieve/create songs."""
    permission_classes = [IsAuthenticated, IsArtist]
    serializer_class = SongSerializer

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request: Request):
        """Returns paginated response with authenticated user's own songs."""
        return get_paginated_songs_list_response(request, self)

    def post(self, request: Request):
        """Creates new song for authenticated user."""
        serializer = SongCreateUpdateDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(artist=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SongDetailsUpdateDeleteView(APIView):
    """Processes GET/PUT/DELETE method to retrieve/update/delete song."""
    permission_classes = [IsAuthenticated, IsSongOwner]
    serializer_class = SongSerializer

    def get(self, request: Request, song_id: int):
        """Returns song identified by 'song_id' parameter."""
        # custom exception handler takes care about ObjectDoesNotExist
        song = Song.objects.annotate(
            is_liked=Exists(
                request.user.liked_songs.filter(pk=OuterRef("pk"))
            )
        ).get(pk=song_id)
        serializer = self.serializer_class(instance=song)
        return Response(serializer.data)

    def put(self, request: Request, song_id: int):
        """
        Updates song identified by 'song_id' parameter.

        Checks object level permissions for Song object
        """
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = SongCreateUpdateDeleteSerializer(
            data=request.data, instance=song, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, song_id: int):
        """
        Deletes identified by 'song_id' parameter.

        Checks object level permissions for Song object
        """
        song = Song.objects.get(pk=song_id)
        self.check_object_permissions(request, song)
        serializer = SongCreateUpdateDeleteSerializer(instance=song)
        song.delete()
        return Response(serializer.data)


class LikedSongsListView(ListAPIView):
    """Processes GET method to obtain user's list of liked songs."""
    permission_classes = [IsAuthenticated]
    serializer_class = SongLikeSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """Returns queryset of liked songs by user."""
        return SongLike.objects.annotate(
            is_liked=Case(default=True, output_field=BooleanField())
        ).filter(profile=self.request.user)


class LikeSongView(APIView):
    """Processes POST/DELETE methods to add/remove song to/from like list."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, song_id: int):
        """Appends Song with 'song_id' to liked song list."""
        song = Song.objects.get(pk=song_id)

        request.user.liked_songs.add(song)
        return Response(
            data={"message": f"Song successful added to liked list"}
        )

    def delete(self, request: Request, song_id: int):
        """Removes Song with 'song_id' from liked song list."""
        song = Song.objects.get(pk=song_id)
        request.user.liked_songs.remove(song)
        return Response(
            data={"message": f"Song successful removed from liked list."}
        )


class SongsNewReleasesView(ListAPIView):
    """Processes GET method to obtain releases of followed Profiles."""
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer
    pagination_class = None

    def get_queryset(self):
        """
        Returns queryset of 10 songs released during last week
        by Profiles which user followed on.
        """
        one_week_ago = timezone.now() - timedelta(days=7)
        return Song.objects.annotate(
            is_followed_on_artist=Exists(
                self.request.user.followings.filter(pk=OuterRef("artist"))
            ),
            is_liked=Exists(
                self.request.user.liked_songs.filter(pk=OuterRef("pk"))
            )
        ).filter(
            is_followed_on_artist=True,
            creation_date__gte=one_week_ago
        ).order_by("-creation_date", "title")[:10]
