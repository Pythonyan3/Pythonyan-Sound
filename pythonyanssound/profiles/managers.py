from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class ProfileManager(BaseUserManager):
    """Profile model manager with email and username as unique identifiers for authentication"""
    def create_user(self, email, username, password, **kwargs):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have an username")
        normalized_email = self.normalize_email(email)
        try:
            validate_email(normalized_email)
        except ValidationError:
            raise ValueError("Email address is incorrect")
        user = self.model(email=normalized_email, username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        return self.create_user(email, username, password, **kwargs)
