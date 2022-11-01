import csv
from pathlib import Path
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from music.domainmodel import genre, album, artist, playlist, review, track, user
from music.adapters.repository import AbstractRepository, RepositoryException
from music.adapters.csvdatareader import *
from music.domainmodel.user import User
# so we can use the trackcsvreader class here
from music.adapters.data import *
import music.authentication.services as auth_services


# Not sure for this one, but I want to use the two csv file in that folder

class MemoryRepository(AbstractRepository):
    def __init__(self, data_path:str):
        album_file_name = str(data_path / "raw_albums_excerpt.csv")
        track_file_name = str(data_path / "raw_tracks_excerpt.csv")
        track_csv_reader = TrackCSVReader(album_file_name, track_file_name)
        track_csv_reader.read_csv_files()
        self.__dataset_of_tracks = track_csv_reader.dataset_of_tracks
        self.__dataset_of_artists = track_csv_reader.dataset_of_artists
        self.__dataset_of_genres = track_csv_reader.dataset_of_genres
        self.__dataset_of_albums = track_csv_reader.dataset_of_albums
        self.__current_page = 0

        self.__dataset_of_users = []
        auth_services.add_user("yifeng123", '521', self)

    def get_page(self):
        return self.__current_page

    def add_user(self, new_user : User):
        self.__dataset_of_users.append(new_user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__dataset_of_users if user.user_name == user_name), None)

    def get_all_users(self):
        return self.__dataset_of_users

    def get_all_tracks(self):
        return self.__dataset_of_tracks

    def get_all_artists(self):
        return self.__dataset_of_artists

    def get_all_genres(self):
        return self.__dataset_of_genres

    def get_all_albums(self):
        return self.__dataset_of_albums

    def add_track(self, new_track):
        state = False
        for e in self.get_all_tracks:
            if e.__eq__(new_track):
                state = True
        if not state:
            self.__dataset_of_tracks.append(new_track)


