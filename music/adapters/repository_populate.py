from pathlib import Path
from music.adapters.repository import AbstractRepository
from music.adapters.csvdatareader import *
from music.domainmodel.user import User
import music.authentication.services as auth_services
import music.authentication.services as auth_services

def populate(data_path: Path, repo: AbstractRepository):
    album_file_name = str(data_path / "raw_albums_excerpt.csv")
    track_file_name = str(data_path / "raw_tracks_excerpt.csv")
    track_csv_reader = TrackCSVReader(album_file_name, track_file_name)
    track_csv_reader.read_csv_files()
    for genre in track_csv_reader.dataset_of_genres:
        repo.add_genre(genre)
    for artist in track_csv_reader.dataset_of_artists:
        repo.add_artist(artist) #implement his is abstractRepo and mem_repo
    for album in track_csv_reader.dataset_of_albums:
        repo.add_album(album)
     #implement his is abstractRepo and mem_repo
     # implement his is abstractRepo and mem_repo
    for track in track_csv_reader.dataset_of_tracks:
        repo.add_track(track)

    auth_services.add_user("yifeng123", '521', repo) #adding a default admit user