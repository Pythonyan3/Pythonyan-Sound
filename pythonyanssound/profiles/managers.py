from typing import Optional

from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email


class ProfileManager(BaseUserManager):
    """Custom user manager for Profile model."""

    def create_user(
            self,
            email: Optional[str],
            username: Optional[str],
            password: Optional[str],
            **extra_fields
    ):
        """
        Implementation of user instance creating with several unique fields.
        """
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have an password")

        normalized_email = self.normalize_email(email)
        validate_email(normalized_email)
        user = self.model(
            email=normalized_email, username=username, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **kwargs):
        """
        Implements superuser creation.

        Sets 'is_stuff' and 'is_superuser' flags to True
        """
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **kwargs)
