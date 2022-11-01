from music.adapters.repository import AbstractRepository


def get_all_tracks(repo: AbstractRepository):
    return repo.get_all_tracks()
    '''the repo is abstractRepo, when we call the method in abstract class, it goes down to
    the concrete implementation class. Because in the init.py, we have define that repo.instance is 
    the concrete implementation of the abstract class.'''


def display_specific_genre_track(genre_name: str, repo: AbstractRepository):
    all_track = get_all_tracks(repo)  # repo.repo_instance.get_all_tracks#
    specific_genre_track_list = list()
    for track in all_track:
        for track_genre in track.genres:
            if genre_name == track_genre.name and track not in specific_genre_track_list:
                specific_genre_track_list.append(track)
    return specific_genre_track_list

def display_specific_artist_track(artist_name: str, repo: AbstractRepository):
    all_track = get_all_tracks(repo)  # repo.repo_instance.get_all_tracks#
    specific_artist_track_list = list()
    for track in all_track:
        if artist_name == track.artist.full_name and track not in specific_artist_track_list:
            specific_artist_track_list.append(track)
    return specific_artist_track_list

def display_specific_album_track(album_title: str, repo: AbstractRepository):
    all_track = get_all_tracks(repo)  # repo.repo_instance.get_all_tracks#
    specific_album_track_list = list()
    for track in all_track:
        if track.album is not None:
            if album_title == track.album.title and track not in specific_album_track_list:
                specific_album_track_list.append(track)
    return specific_album_track_list

def comment_get_user(username, repo):
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException
    return user

def search_track(id, title, repo):
    all_track = get_all_tracks(repo)
    for track in all_track:
        if track.title == title and track.track_id == int(id):
            return track
    return None

class UnknownUserException(Exception):
    pass

def get_user(username, repo):
    return repo.get_user(username)


def add_to_fav(username, track, repo):
    user = repo.get_user(username)
    user.add_liked_track(track)
