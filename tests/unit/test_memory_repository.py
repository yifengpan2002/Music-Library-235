import pytest

from music import create_app
from music.adapters import memory_repository
from music.adapters.memory_repository import MemoryRepository
from music.domainmodel.user import User
from music.domainmodel.track import Track

from utils import get_project_root

TEST_DATA_PATH = get_project_root() / "tests" / "data"


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository(TEST_DATA_PATH)
    return repo


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,  # Set to True during testing.
        'TEST_DATA_PATH': TEST_DATA_PATH,  # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False  # test_client will not send a CSRF token, so disable validation.
    })
    '''so right now we have a clicent that can interact with our website'''
    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    def login(self, user_name='yifeng123', password='123'):
        return self.__client.post(
            '/login',
            data={'user_name': user_name, 'password': password}
        )

    def logout(self):
        return self.__client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)


def test_repository_can_add_a_user(in_memory_repo):
    user = User(len(in_memory_repo.get_all_users), 'dave', '123456789')
    previous_len = len(in_memory_repo.get_all_users)
    in_memory_repo.add_user(user)
    after = len(in_memory_repo.get_all_users)

    assert in_memory_repo.get_user('dave') is user
    assert previous_len != after


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('yifeng123')
    assert user == User(0, 'yifeng123', '521')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_review_count(in_memory_repo):
    user = in_memory_repo.get_user('yifeng123')
    assert len(user.reviews) == 0


def test_repository_can_add_track(in_memory_repo):
    track = Track(202011, "woxihuanjiejie")
    before = len(in_memory_repo.get_all_tracks)
    in_memory_repo.add_track(track)
    after = len(in_memory_repo.get_all_tracks)
    assert before != after


def test_repository_add_invalid_track(in_memory_repo):
    track = Track(2, "woxihuanjiejie")
    before = len(in_memory_repo.get_all_tracks)
    in_memory_repo.add_track(track)
    after = len(in_memory_repo.get_all_tracks)
    assert before == after
