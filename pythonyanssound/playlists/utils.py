

def playlist_cover_upload_folder(playlist_instance, filename: str):
    return f"playlists/{playlist_instance.owner.id}/covers/{filename}"
