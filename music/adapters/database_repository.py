from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.orm import scoped_session
from music.domainmodel.user import User
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.album import Album
from music.domainmodel.artist import Artist

from music.domainmodel import album, artist, genre,playlist,review,track,user
from music.adapters.repository import AbstractRepository


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_track(self, new_track):
        with self._session_cm as scm:
            scm.session.merge(new_track)
            scm.commit()
    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.merge(user)
            scm.commit()
    def get_all_users(self):
        users = self._session_cm.session.query(User).all()
        return users
    def get_all_albums(self):
        albums = self._session_cm.session.query(Album).all()
        return albums
    def get_all_artists(self):
        artists = self._session_cm.session.query(Artist).all()
        return artists
    def get_all_genres(self):
        genres = self._session_cm.session.query(Genre).all()
        return genres
    def get_all_tracks(self):
        tracks = self._session_cm.session.query(Track).all()
        return tracks

    def get_page(self): # we dont use this anyway in our browse function
        return 0
    def get_user(self, user_name: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == user_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user
    def add_artist(self, artist):
        with self._session_cm as scm:
            scm.session.merge(artist)
            scm.commit()
    def add_genre(self, genre):
        with self._session_cm as scm:
            scm.session.merge(genre)
            scm.commit()
    def add_album(self, album):
        with self._session_cm as scm:
            scm.session.merge(album)
            scm.commit()
