

def playlist_cover_upload_folder(playlist_instance, filename: str):
    """Returns path to upload Playlist cover image."""
    return f"playlists/{playlist_instance.owner.id}/covers/{filename}"
