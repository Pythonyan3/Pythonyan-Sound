from django.contrib.auth.models import AbstractBaseUser
from django.db.models import CharField, ImageField, TextField, BooleanField

from .managers import ProfileManager


class Profile(AbstractBaseUser):
    """Custom user model. Fields 'password, last_login are inherited from AbstractBaseUser"""
    username = CharField(max_length=255, unique=True)
    email = CharField(max_length=255, unique=True)
    photo = ImageField(upload_to="images", blank=True)
    biography = TextField(blank=True)
    is_active = BooleanField(default=True)
    is_artist = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'password', ]

    objects = ProfileManager()

    class Meta:
        db_table = "profiles"

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_active
