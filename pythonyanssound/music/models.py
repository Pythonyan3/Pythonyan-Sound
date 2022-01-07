from django.core.validators import FileExtensionValidator
from django.db.models import (
    Model, CharField, FileField, ImageField, ForeignKey, CASCADE,
    IntegerField, ManyToManyField, DateTimeField
)

from music.utils import song_upload_folder, song_cover_upload_folder
from pythonyanssound.validators import (
    validate_image_resolution, validate_file_size
)


class Genre(Model):
    """Describes music genre."""
    # Primitive fields
    genre = CharField(
        verbose_name="Genre name.",
        max_length=255,
        blank=False
    )

    def __str__(self):
        """String representation of Genre."""
        return self.genre

    class Meta:
        """Additional settings for model."""
        db_table = "genres"


class Song(Model):
    """Describes song instance owned by user with is_artist flag."""
    # Primitive fields
    title = CharField(
        verbose_name="Song title name.",
        max_length=255,
        blank=False
    )
    audio = FileField(
        verbose_name="Song audio file link (saved to S3 bucket).",
        validators=(
            FileExtensionValidator(allowed_extensions=["mp3"]),
            validate_file_size
        ),
        upload_to=song_upload_folder
    )
    cover = ImageField(
        verbose_name="Song cover image file link (saved to S3 bucket).",
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=song_cover_upload_folder
    )
    creation_date = DateTimeField(
        verbose_name="Song creation (uploading) date.",
        auto_now_add=True
    )
    # ForeignKey fields
    genre = ForeignKey(
        verbose_name="Song's genre instance.",
        to=Genre,
        on_delete=CASCADE,
        related_name="songs"
    )
    artist = ForeignKey(
        verbose_name="Song's owner instance.",
        to="profiles.Profile",
        on_delete=CASCADE,
        related_name="songs"
    )
    # M2M fields
    listens = ManyToManyField(
        verbose_name="List of songs listens by Profiles.",
        to="profiles.Profile",
        through='Listen',
        related_name="listens"
    )

    def __str__(self):
        """String representation of Song."""
        return f"{self.artist} - {self.title}"

    class Meta:
        """Additional settings for model."""
        db_table = "music"


class Listen(Model):
    """
    Listen like model describes relation between Profile and Song
    (Profile have listened Song).

    Model used as separate table for describing relation
    Includes additional info about Listen such as:
        - count: number of song listens.
    """
    # Primitive fields
    count = IntegerField(
        verbose_name="Number of song listens.",
        default=0
    )
    # TODO fix wrong 'related_name'
    # ForeignKey fields
    profile = ForeignKey(
        verbose_name="Profile who have listened the song.",
        to="profiles.Profile",
        on_delete=CASCADE,
        related_name="profile"
    )
    # TODO fix wrong 'related_name'
    song = ForeignKey(
        verbose_name="Song instance which have been listened by Profile.",
        to=Song,
        on_delete=CASCADE,
        related_name="song"
    )

    class Meta:
        """Additional settings for model."""
        db_table = "songs_listens"
