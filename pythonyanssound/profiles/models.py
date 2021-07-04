from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import CharField, ImageField, TextField, ManyToManyField, BooleanField, Model, ForeignKey, \
    CASCADE, DateTimeField

from pythonyanssound.validators import validate_image_resolution, validate_file_size
from .managers import ProfileManager
from .utils import profile_photo_upload_folder


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    Fields 'password', 'last_login' are inherited from AbstractBaseUser
    Uses custom manager
    """
    username = CharField(max_length=255, unique=True)
    email = CharField(max_length=255, unique=True)
    photo = ImageField(
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=profile_photo_upload_folder
    )
    biography = TextField(blank=True)
    # set model name as string to avoid circular import
    liked_songs = ManyToManyField(
        "music.Song",
        through="profiles.SongLike",
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


class SongLike(Model):

    profile = ForeignKey("profiles.Profile", on_delete=CASCADE, related_name="liked_songs_through")
    song = ForeignKey("music.Song", on_delete=CASCADE, related_name="liked_profiles_through")

    like_date = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "songs_likes"
        ordering = ("-like_date",)
