from django.db.models import Model, CharField, ImageField, ForeignKey, CASCADE, ManyToManyField


class Playlist(Model):
    title = CharField(max_length=255, blank=False)
    cover = ImageField(blank=True)
    owner = ForeignKey("profiles.Profile", on_delete=CASCADE)
    songs = ManyToManyField("music.Song", db_table="playlists_songs", related_name="playlists", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "playlists"
