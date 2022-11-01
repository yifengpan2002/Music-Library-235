import pytest

from music import create_app
from music.adapters import memory_repository
from music.adapters.memory_repository import MemoryRepository
from flask import session
from music.domainmodel.user import User
from utils import get_project_root
import music.authentication.services as auth_services
import music.browse.services as browse_services
import music.favorites.services as fav_services
from music.adapters.csvdatareader import TrackCSVReader

TEST_DATA_PATH = get_project_root() / "tests" / "data"


@pytest.fixture
def in_memory_repo2():
    repo = MemoryRepository(TEST_DATA_PATH)
    album_file = str(TEST_DATA_PATH) + '/raw_albums_test.csv'
    track_file = str(TEST_DATA_PATH) + '/raw_tracks_test.csv'
    track_csv_reader = TrackCSVReader(album_file, track_file)
    track_csv_reader.read_csv_files()
    repo.__dataset_of_tracks = track_csv_reader.dataset_of_tracks
    repo.__dataset_of_albums = track_csv_reader.dataset_of_albums
    return repo

@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository(TEST_DATA_PATH)
    return repo

@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,                                # Set to True during testing.
        'TEST_DATA_PATH': TEST_DATA_PATH,               # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False                       # test_client will not send a CSRF token, so disable validation.
    })
    '''so right now we have a clicent that can interact with our website'''
    return my_app.test_client()

class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    def login(self, user_name='yifeng123', password='521'):
        return self.__client.post(
            '/login',
            data={'user_name': user_name, 'password': password}
        )

    def logout(self):
        return self.__client.get('/logout')

@pytest.fixture
def auth(client):
    return AuthenticationManager(client)

def test_auth_get_user(in_memory_repo):
    username = "yifeng123"
    user_as_dict = auth_services.get_user(username, in_memory_repo)
    assert user_as_dict['user_name'] == username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')

def test_auth_get_invalid_user(in_memory_repo):
    username = "yifeng321"
    password = "dfadfa"
    with pytest.raises(auth_services.UnknownUserException):
        auth_services.get_user(username, in_memory_repo)

def test_auth_add_user(in_memory_repo):
    username = "yifeng321"
    password = "dfadfa"
    previous = len(in_memory_repo.get_all_users)
    auth_services.add_user(username,password,in_memory_repo)
    after = len(in_memory_repo.get_all_users)
    assert previous != after

def test_auth_add_invalid_user(in_memory_repo):
    username = "yifeng123"
    password = "dfadfa"
    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(username,password, in_memory_repo)

def test_auth_invalid_validate_user(in_memory_repo):
    username = "yifeng123"
    password = "dfadfa"
    with pytest.raises(auth_services.AuthenticationException):
        auth_services.validate_user(username,password, in_memory_repo)

def test_auth_validate_user_with_no_user(in_memory_repo):
    username = "yifeng1235"
    password = "dfadfa"
    with pytest.raises(auth_services.UnknownUserException):
        auth_services.validate_user(username,password, in_memory_repo)

def test_browse_get_all_user(in_memory_repo):
    assert len(browse_services.get_all_tracks(in_memory_repo)) != 0

def test_browse_display_specific_genre_track(in_memory_repo2):
    genre_track = browse_services.display_specific_genre_track("Avant-Garde",in_memory_repo2)
    assert  len(genre_track) != 0

def test_browse_display_specific_genre_track_with_invalid_input(in_memory_repo):
    artist_track = browse_services.display_specific_genre_track("ILoveUJian",in_memory_repo)
    assert  len(artist_track) == 0

def test_browse_display_specific_artist_track(in_memory_repo2):
    artist_track = browse_services.display_specific_artist_track("AWOL",in_memory_repo2)
    assert  len(artist_track) != 0

def test_browse_display_specific_artist_track_with_invalid_input(in_memory_repo):
    genre_track = browse_services.display_specific_artist_track("YifengPan",in_memory_repo)
    assert  len(genre_track) == 0

def test_browse_display_specific_album_track(in_memory_repo2):
    album_track = browse_services.display_specific_album_track("Niris",in_memory_repo2)
    assert  len(album_track) != 0

def test_browse_display_specific_album_track_with_invalid_input(in_memory_repo):
    album_track = browse_services.display_specific_album_track("Owanimama",in_memory_repo)
    assert  len(album_track) == 0

def test_comment_get_user(in_memory_repo):
    assert type(browse_services.comment_get_user("yifeng123",in_memory_repo)) == User

def test_comment_get_user_with_invalid_user(in_memory_repo):
    with pytest.raises(browse_services.UnknownUserException):
        assert browse_services.comment_get_user("Christine",in_memory_repo)
