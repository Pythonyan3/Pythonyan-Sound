from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Profile


class ProfileAuthBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        try:
            validate_email(username)
            profile = Profile.objects.filter(email=username).first()
        except ValidationError:
            profile = Profile.objects.filter(username=username).first()
        if profile and profile.check_password(password):
            return profile
        return None

    def get_user(self, user_id):
        return Profile.objects.filter(pk=user_id).first()
