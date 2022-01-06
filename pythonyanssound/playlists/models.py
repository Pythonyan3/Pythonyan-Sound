from django.db.models import (
    Model, CharField, ImageField, ForeignKey, CASCADE, ManyToManyField,
    DateTimeField
)

from playlists.utils import playlist_cover_upload_folder
from pythonyanssound.validators import (
    validate_image_resolution, validate_file_size
)


class Playlist(Model):
    """Describes Playlist instance for users to group songs."""
    # Primitive fields
    title = CharField(
        verbose_name="Playlist title name.",
        max_length=255,
        blank=False
    )
    cover = ImageField(
        verbose_name="Playlist cover image link (saved to S3 bucket).",
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=playlist_cover_upload_folder
    )
    creation_date = DateTimeField(
        verbose_name="Playlist creation date.",
        auto_now_add=True
    )
    # ForeignKey fields
    owner = ForeignKey(
        verbose_name="Profile instance which owns playlist.",
        to="profiles.Profile",
        on_delete=CASCADE,
        related_name="playlists"
    )
    # M2M fields
    # TODO remove it (can be accessed by related_name from through Model)
    songs = ManyToManyField(
        verbose_name="List of songs in playlist.",
        to="music.Song",
        through="playlists.SongInPlaylist",
        related_name="playlists",
        blank=True
    )

    def __str__(self):
        """String representation of Playlist."""
        return self.title

    class Meta:
        """Additional settings for model."""
        db_table = "playlists"


class SongInPlaylist(Model):
    """
    Describes relation between Playlist and Song models
    (Song is included to playlist/Playlist contains song).

    Model used as separate table to describe relation
    Extend common M2M relation with 'adding_date'
    """
    # Primitive fields
    adding_date = DateTimeField(
        verbose_name="Date of Song adding to Playlist.",
        auto_now_add=True
    )
    # ForeignKey fields
    playlist = ForeignKey(
        verbose_name="Playlist instance which contains song.",
        to="playlists.Playlist",
        on_delete=CASCADE,
        related_name="songs_through"
    )
    song = ForeignKey(
        verbose_name="Song instance added to Playlist",
        to="music.Song",
        on_delete=CASCADE,
        related_name="playlists_through"
    )

    class Meta:
        """Additional settings for model."""
        db_table = "playlists_songs"
        ordering = ("-adding_date",)
