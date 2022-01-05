from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.request import Request

from .models import Profile


class ProfileAuthBackend(BaseBackend):
    """Custom authentication backend."""

    def authenticate(self, request: Request, **kwargs) -> Optional[Profile]:
        """Implements authenticate user by username or email address."""
        username = kwargs['username']
        password = kwargs['password']
        try:
            # check if entered credential is email address
            validate_email(username)
            profile = Profile.objects.filter(email=username).first()
        except ValidationError:
            # credential isn't email address then it might be username
            profile = Profile.objects.filter(username=username).first()
        if profile and profile.check_password(password):
            return profile
        return None

    def get_user(self, user_id: int) -> Optional[Profile]:
        """Implements get user with custom model (Profile)."""
        return Profile.objects.filter(pk=user_id).first()
