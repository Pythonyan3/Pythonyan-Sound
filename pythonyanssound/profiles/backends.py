from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Profile


class ProfileAuthBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        get_kwargs = dict()
        # check what field use to auth, email or username
        try:
            validate_email(username)
            get_kwargs.setdefault('email', username)
        except ValidationError:
            get_kwargs.setdefault('username', username)
        # try to get user and check password
        try:
            profile = Profile.objects.get(**get_kwargs)
            if profile.check_password(password):
                return profile
        except Profile.DoesNotExist:
            pass
        return None

    def get_user(self, user_id):
        try:
            return Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return None
