from django.contrib import admin

from music.models import Genre, Song


admin.site.register(Genre)
admin.site.register(Song)
