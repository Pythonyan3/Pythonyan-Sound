from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_image_file_extension
from django.db.models import CharField, ImageField, TextField, ManyToManyField, BooleanField

from pythonyanssound.validators import validate_image_resolution, validate_file_size
from .managers import ProfileManager


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    Fields 'password', 'last_login' are inherited from AbstractBaseUser
    Uses custom manager
    """
    username = CharField(max_length=255, unique=True, error_messages={
        "blank": "Username field cannot be empty",
        "unique": "User with this username already exists"
    })
    email = CharField(max_length=255, unique=True, error_messages={
        "blank": "Email field cannot be empty",
        "unique": "User with this email address already exists"
    })
    photo = ImageField(upload_to="images", blank=True, validators=(validate_image_resolution, validate_file_size))
    biography = TextField(blank=True)
    # set model name as string to avoid circular import
    liked_songs = ManyToManyField(
        "music.Song",
        db_table="songs_likes",
        related_name="liked_profiles",
        blank=True
    )
    liked_playlists = ManyToManyField(
        "playlists.Playlist",
        db_table="playlists_likes",
        related_name="liked_profiles",
        blank=True
    )
    followings = ManyToManyField(
        "profiles.Profile",
        db_table="followings",
        related_name="followers",
        blank=True
    )
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
