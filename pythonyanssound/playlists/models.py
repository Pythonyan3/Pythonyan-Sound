from django.db.models import Model, CharField, ImageField, ForeignKey, CASCADE, ManyToManyField, DateTimeField

from playlists.utils import playlist_cover_upload_folder
from pythonyanssound.validators import validate_image_resolution, validate_file_size


class Playlist(Model):
    title = CharField(max_length=255, blank=False)
    cover = ImageField(
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=playlist_cover_upload_folder
    )
    creation_date = DateTimeField(auto_now_add=True)
    owner = ForeignKey("profiles.Profile", on_delete=CASCADE, related_name="playlists")
    songs = ManyToManyField("music.Song", through="playlists.SongInPlaylist", related_name="playlists", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "playlists"


class SongInPlaylist(Model):

    playlist = ForeignKey("playlists.Playlist", on_delete=CASCADE, related_name="songs_through")
    song = ForeignKey("music.Song", on_delete=CASCADE, related_name="playlists_through")
    adding_date = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "playlists_songs"
        ordering = ("-adding_date",)
