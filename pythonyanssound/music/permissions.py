from rest_framework.permissions import BasePermission, SAFE_METHODS

from music.models import Song


class IsSongOwner(BasePermission):
    """Custom permission class for Song views."""
    def has_object_permission(self, request, view, obj: Song):
        """
        Returns 'True' if request method is safe or
        song owner instance equals to request user instance.
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.artist == request.user


class IsArtist(BasePermission):
    """Custom permission class to check is user an artist."""
    def has_permission(self, request, view):
        """
        Returns 'True' if request method is safe or
        request user instance has 'is_artist' flag.
        """
        if request.method not in SAFE_METHODS:
            return request.user.is_artist
        return True
