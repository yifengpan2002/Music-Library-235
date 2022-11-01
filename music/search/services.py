from music.adapters.repository import AbstractRepository
from music.browse.services import get_all_tracks


def searchTracks(search: str, repo: AbstractRepository):
    all_track = get_all_tracks(repo)
    searched = []
    for track in all_track:
        if search.lower() in track.title.lower():
            searched.append(track)
        if track.album is not None:
            if search.lower() == track.album.title.lower():
                searched.append(track)
        if search.lower() == track.artist.full_name.lower():
            searched.append(track)
        for genre in track.genres:
            if search.lower() == genre.name.lower():
                searched.append(track)

    return searched
