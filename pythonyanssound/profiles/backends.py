from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Profile


class ProfileAuthBackend(BaseBackend):
    """
    Custom authentication backend
    Allow authenticate user by username or email address
    """
    def authenticate(self, request, **kwargs):
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

    def get_user(self, user_id):
        return Profile.objects.filter(pk=user_id).first()
