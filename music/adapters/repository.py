import abc
from typing import List
from datetime import date

from music.domainmodel import genre, album, artist, playlist, review, track, user

'''
all the abstract methods defined here do not necessary needed to define in mem_repo, it can define in other services
but remember to import the abstract repository tho
'''
repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get_user(self):
        raise NotImplementedError

    @abc.abstractmethod
    def add_user(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_users(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_page(self):
        raise NotImplementedError

    # this is used for the marking of current page. Just like the cusor in covid app
    @abc.abstractmethod
    def get_all_tracks(self):
        # gets all the track in the provided csv file
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_artists(self):
        # gets all the track in the provided csv file
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_genres(self):
        # gets all the track in the provided csv file
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_albums(self):
        # gets all the track in the provided csv file
        raise NotImplementedError

    @abc.abstractmethod
    def add_track(self, new_track):
        raise NotImplementedError