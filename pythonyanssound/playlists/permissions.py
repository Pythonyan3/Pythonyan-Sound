from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from playlists.models import Playlist


class IsPlaylistOwner(BasePermission):
    """Custom permission class for playlist views."""

    def has_object_permission(self, request: Request, view, obj: Playlist):
        """
        Returns 'True' if request method is safe or
        playlist owner instance equals to request user instance.
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
