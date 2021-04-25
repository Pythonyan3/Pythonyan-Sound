from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from playlists.models import Playlist


class IsPlaylistOwner(BasePermission):
    def has_object_permission(self, request: Request, view, obj: Playlist):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
