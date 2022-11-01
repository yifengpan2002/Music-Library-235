from music import AbstractRepository


def get_user(username, repo):
    return repo.get_user(username)


def get_all_tracks(repo: AbstractRepository):
    return repo.get_all_tracks()


def find_track(track, track_list):
    for i in track_list:
        if str(i) == track:
            return i
