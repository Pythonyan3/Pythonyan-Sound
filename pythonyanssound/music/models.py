from django.core.validators import FileExtensionValidator
from django.db.models import Model, CharField, FileField, ImageField, ForeignKey, CASCADE, IntegerField, \
    ManyToManyField, DateTimeField

from music.utils import song_upload_folder, song_cover_upload_folder
from pythonyanssound.validators import validate_image_resolution, validate_file_size


class Genre(Model):
    """Genre model. Represents music genre, used as foreign key"""
    genre = CharField(max_length=255, blank=False)

    def __str__(self):
        return self.genre

    class Meta:
        db_table = "genres"


class Song(Model):
    title = CharField(max_length=255, blank=False)

    audio = FileField(
        validators=(FileExtensionValidator(allowed_extensions=["mp3"]),
                    validate_file_size),
        upload_to=song_upload_folder
    )
    cover = ImageField(
        blank=True,
        validators=(validate_image_resolution, validate_file_size),
        upload_to=song_cover_upload_folder
    )
    genre = ForeignKey(Genre, on_delete=CASCADE, related_name="songs")
    creation_date = DateTimeField(auto_now_add=True)
    # set model name as string to avoid circular import
    artist = ForeignKey("profiles.Profile", on_delete=CASCADE, related_name="songs")
    # many to many relation with custom table
    listens = ManyToManyField("profiles.Profile", through='Listen', related_name="listens")

    def __str__(self):
        return f"{self.artist} - {self.title}"

    class Meta:
        db_table = "music"


class Listen(Model):
    """
    Listen model specified many to many relations between Profile and Song
    Contain count of listens of Song by Profile
    """
    profile = ForeignKey("profiles.Profile", on_delete=CASCADE, related_name="profile")
    song = ForeignKey(Song, on_delete=CASCADE, related_name="song")
    count = IntegerField(default=0)

    class Meta:
        db_table = "songs_listens"
