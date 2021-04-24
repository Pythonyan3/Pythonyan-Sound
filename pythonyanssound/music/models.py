from django.db.models import Model, CharField, FileField, ImageField, ForeignKey, CASCADE, IntegerField, ManyToManyField


class Genre(Model):
    """Genre model. Represents music genre, used as foreign key"""
    genre = CharField(max_length=255, blank=False)

    def __str__(self):
        return self.genre

    class Meta:
        db_table = "genres"


class Song(Model):
    title = CharField(max_length=255, blank=False)
    # TODO add s3 storage
    audio = FileField()
    cover = ImageField()
    genre = ForeignKey(Genre, on_delete=CASCADE)
    # set model name as string to avoid circular import
    artist = ForeignKey("profiles.Profile", on_delete=CASCADE, related_name="artist")
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
