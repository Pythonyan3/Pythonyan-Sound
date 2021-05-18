from django.db.models import Exists, OuterRef
from rest_framework.request import Request

from music.models import Song
from music.serializers import SongSerializer
from pythonyanssound.pagination import CustomPageNumberPagination


def get_paginated_songs_list_response(request: Request, view):
    # annotate songs with current user's likes
    songs = Song.objects.filter(artist=request.user).annotate(
        is_liked=Exists(request.user.liked_songs.filter(pk=OuterRef("pk")))
    ).order_by("title")

    paginator = CustomPageNumberPagination()
    paged_songs = paginator.paginate_queryset(songs, request, view)

    serializer = SongSerializer(instance=paged_songs, many=True, context=view.get_serializer_context())

    return paginator.get_paginated_response(serializer.data)
