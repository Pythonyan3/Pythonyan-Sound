from django.db.models import Model, CharField, ImageField, ForeignKey, CASCADE


class Playlist(Model):
    title = CharField(max_length=255, blank=False)
    cover = ImageField(blank=True)
    owner = ForeignKey("profiles.Profile", on_delete=CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "playlists"
