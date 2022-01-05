from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import (
    CharField, ImageField, TextField, ManyToManyField, BooleanField, Model,
    ForeignKey, CASCADE, DateTimeField
)

from pythonyanssound.validators import (
    validate_image_resolution, validate_file_size
)
from .managers import ProfileManager
from .utils import profile_photo_upload_folder


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    Custom Django User model implementation.

    Fields 'password', 'last_login' are inherited from AbstractBaseUser
    Uses custom manager for new Profile creation
    """
    # Primitive fields
    username = CharField(
        verbose_name="User's unique username.",
        max_length=255,
        unique=True
    )
    email = CharField(
        verbose_name="User's unique email address.",
        max_length=255,
        unique=True
    )
    photo = ImageField(
        verbose_name="User's photo link (saved to S3 bucket).",
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=profile_photo_upload_folder
    )
    biography = TextField(
        verbose_name="Some text about user.",
        blank=True
    )
    is_active = BooleanField(
        verbose_name="Is user active flag.", default=True
    )
    is_artist = BooleanField(
        verbose_name="Is user artist flag "
                     "(can upload songs and appear in search as 'Artist').",
        default=False
    )
    is_verified = BooleanField(
        verbose_name="Has user confirmed his email address.",
        default=False
    )
    is_staff = BooleanField(
        verbose_name="Is user staff flag.",
        default=False
    )
    # M2M fields
    liked_songs = ManyToManyField(
        verbose_name="List of user's liked songs.",
        to="music.Song",
        through="profiles.SongLike",
        related_name="liked_profiles",
        blank=True
    )
    liked_playlists = ManyToManyField(
        verbose_name="List of user's liked playlists.",
        to="playlists.Playlist",
        db_table="playlists_likes",
        related_name="liked_profiles",
        blank=True
    )
    followings = ManyToManyField(
        verbose_name="List of user's followings.",
        to="profiles.Profile",
        db_table="followings",
        related_name="followers",
        blank=True
    )

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'password', ]

    objects = ProfileManager()

    class Meta:
        """Additional settings for model."""
        db_table = "profiles"

    def __str__(self) -> str:
        """Returns Profile username."""
        return str(self.username)


class SongLike(Model):
    """
    Song like model describes relation between Profile and Song
    (Profile likes Song).

    Model used as separate table for describing relation
    Includes additional info about SongLike such as:
        - like_date: date of song like.
    """
    # Primitive fields
    like_date = DateTimeField(
        verbose_name="Date of song like.",
        auto_now_add=True
    )
    # ForeignKey fields
    profile = ForeignKey(
        verbose_name="Profile who liked song.",
        to="profiles.Profile",
        on_delete=CASCADE,
        related_name="liked_songs_through"
    )
    song = ForeignKey(
        verbose_name="Song liked by profile.",
        to="music.Song",
        on_delete=CASCADE,
        related_name="liked_profiles_through"
    )

    class Meta:
        """Additional settings for model."""
        db_table = "songs_likes"
        ordering = ("-like_date",)
