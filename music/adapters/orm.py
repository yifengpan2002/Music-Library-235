from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship, synonym
from music.domainmodel import user
from music.domainmodel import track
from music.domainmodel import genre
from music.domainmodel import album
from music.domainmodel import artist
from music.domainmodel import playlist
from music.domainmodel import review
from music.domainmodel import *

metadata = MetaData()

user_table = Table(#review should contain user id not otherway around
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    # Column('review_id', ForeignKey('review.id')), this one not important
    # Column('like_track_id', ForeignKey('playlist.id'))
)

track_table = Table(
    'track', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('track_url', String(255), nullable=True),
    Column('duration', Integer, unique=False, nullable=True),
    Column('album_id', ForeignKey('album.id')),
    Column('artist_id', ForeignKey('artist.id')),
    Column('genre_id', ForeignKey('genre.id'))
)

genre_table = Table(
    'genre', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), unique=True, nullable=False)
)

album_table = Table(
    'album', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('album_url', String(255), unique=True, nullable=False),
    Column('album_type', String(255)),
    Column('release_year', Integer,unique=False, nullable=True)
)

artist_table = Table(
    'artist', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), unique=True, nullable=False)
)

playlist_table = Table(
    'playlist', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id'), nullable=False),
    Column('track_id', ForeignKey('track.id'), nullable=False)
)

review_table = Table(
    'review', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('review_text', String(255), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('timestamp', DateTime, nullable=False),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False)
)

# For many-to-many relationships

track_review_table = Table(
    'track_review', metadata,
    Column('review_id', Integer, ForeignKey('review.id'), primary_key=True),
    Column('track_id', Integer, ForeignKey('track.id'), primary_key=True)
)

track_genre_table = Table(
    'track_genre', metadata,
    Column('track_id', Integer, ForeignKey('genre.id'), primary_key=True, nullable=False),
    Column('genre_id', Integer, ForeignKey('track.id'), primary_key=True, nullable=False)
)

playlist_track_table = Table(
    'playlist_track', metadata,
    Column('playlist_id', Integer, ForeignKey('playlist.id'), primary_key=True, nullable=False),
    Column('track_id', Integer, ForeignKey('track.id'), primary_key=True, nullable=False)
)


def map_model_to_tables():
    mapper(user.User, user_table, properties={
        '_User__user_name': user_table.c.username,
        '_User__password': user_table.c.password,
        '_User__reviews': relationship(review.Review, backref='_Review__user'),
        '_User__liked_tracks': relationship(playlist.PlayList, backref='_PlayList__user')
    }) #playlist and review must have a user property to back ref into

    mapper(track.Track, track_table, properties={
        '_Track__track_id': track_table.c.id,
        '_Track__title': track_table.c.title,
        '_Track__track_duration': track_table.c.duration,
        '_Track__track_url': track_table.c.track_url,

        '_Track__album': relationship(album.Album, backref='_Album__track'),
        '_Track__artist': relationship(artist.Artist),#, backref='_Artist__track'),
        '_Track__genres': relationship(genre.Genre, secondary=track_genre_table,
                                       back_populates='_Genre__track'),
        '_Track__comment': relationship(review.Review, secondary=track_review_table, backref="_Review__track"),
        '_Track__playlist': relationship(playlist.PlayList, secondary=playlist_track_table,
                                       back_populates='_Playlist__list_of_tracks'),
    })
    mapper(review.Review, review_table, properties={
        '_Review__rating': review_table.c.rating,
        '_Review__review_text': review_table.c.review_text,
        '_Review__timestamp': review_table.c.timestamp,
        #'_Review__track': relationship(track.Track, secondary=track_review_table, back_populates='_Track__comment')
        # '_Review__user': relationship(user.User, backref='_User__reviews')
    })
    mapper(album.Album, album_table, properties={
        '_Album__title': album_table.c.title,
        '_Album__album_type': album_table.c.album_type,
        '_Album__album_url': album_table.c.album_url,
        '_Album__album_id': album_table.c.id,
        '_Album__release_year': album_table.c.release_year
        # '_Album__track': relationship(track.Track, backref='_Track__album')
    })
    mapper(artist.Artist, artist_table, properties={
        '_Artist__artist_id': artist_table.c.id,
        '_Artist__full_name': artist_table.c.name,
        # '_Artist__track': relationship(track.Track, backref='_Track__artist')
    })
    mapper(genre.Genre, genre_table, properties={
        '_Genre__genre_id': genre_table.c.id,
        '_Genre__name': genre_table.c.name,
        '_Genre__track': relationship(track.Track, secondary=track_genre_table,
                                     back_populates='_Track__genres')
    })
    mapper(playlist.PlayList, playlist_table, properties={
        '_Playlist__list_of_tracks': relationship(track.Track, secondary=playlist_track_table)
    })
