from rest_framework.permissions import BasePermission, SAFE_METHODS

from music.models import Song


class IsSongOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Song):
        if request.method in SAFE_METHODS:
            return True
        return obj.artist == request.user


class IsArtist(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return request.user.is_artist
        return True
