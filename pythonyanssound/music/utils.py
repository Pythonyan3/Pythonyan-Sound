

def song_upload_folder(song_instance, filename: str):
    """Returns path to upload Song audio file."""
    return f'music/{song_instance.artist.pk}/songs/{filename}'


def song_cover_upload_folder(song_instance, filename: str):
    """Returns path to upload Song cover image file."""
    return f'music/{song_instance.artist.pk}/covers/{filename}'
