

def song_upload_folder(song_instance, filename: str):
    return f'music/{song_instance.artist.pk}/songs/{filename}'


def song_cover_upload_folder(song_instance, filename: str):
    return f'music/{song_instance.artist.pk}/covers/{filename}'
