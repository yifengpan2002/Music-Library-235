import pytest

from flask import session
from music import create_app
from music.adapters import memory_repository
from music.adapters.memory_repository import MemoryRepository

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
    '''so right now we have a client that can interact with our website'''
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

    '''this does seem like working, i guess its because we dont have user.csv and corresponding method in mem-repo to 
    read user password and username so we cannot do the test for it '''


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------Test Cases Starts Here -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid user name and password.
    response = client.post(
        '/register',
        data={'user_name': 'yifeng', 'password': '521'}
    )
    assert b'you have successfully registered' in response.data

@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Your user name is required'),
        ('cj', '', b'Your user name is too short'),
        ('test', '', b'Your password is required'),
        ('yifeng', '521', b'you have successfully registered'),
        ('yifeng123', 'Test#6^0', b'Your user name is already taken - please supply another'),
))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    # messages.
    response = client.post(
        '/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage.

    response = auth.login()
    status_code2 = response.status_code
    assert status_code2 == 302 #meaning the user has successfully login
    #assert response.headers['Location'] == 'http://localhost/'



    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['user_name'] == 'yifeng123'


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session

def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'Music is generally defined as the art of arranging sound' in response.data

def test_comment(client, auth):
    # Login a user.
    auth.login()

    # Check that we can retrieve the comment page.
    response = client.get('/comment?id=2&title=Food')
    assert response.status_code == 200
    response = client.post(
        '/comment?id=2&title=Food',
        data={'comment': 'Who needs this music?', 'rating': 2}
    )
    assert b'Who needs this music?' in response.data

def test_comment_without_login(client, auth):
    # Login a user.

    # Check that we can retrieve the comment page.
    response = client.get('/comment?id=2&title=Food')

    response = client.post(
        '/comment?id=2&title=Food',
        data={'comment': 'Who needs this music?', 'rating': 2}
    )
    assert response.headers['Location'] == '/login'


@pytest.mark.parametrize(('rating', 'messages'), (
        (9, (b'Rating number must be 0 - 5')),
        (4, (b'Rating = 4')),
        (5, (b'Rating = 5')),
        (-1, (b'Rating number must be 0 - 5')),
        (None, (b'Rating number must be 0 - 5')),
))
def test_comment_with_invalid_rating(client, auth, rating, messages):
    # Login a user.
    auth.login()

    # Attempt to comment on an article.
    response = client.post(
        '/comment?id=2&title=Food',
        data={'rating': rating, 'comment': "this is good"}
    )
    assert response.status_code == 200 #this means we haven post correctly
    # Check that supplying invalid comment text generates appropriate error messages.
    for message in messages:
        assert message in response.data

@pytest.mark.parametrize(('comment', 'messages'), (
        ('Hy', (b'Your comment is too short')),
        ('', (b'Your comment is too short')),
        ('Hyadfadf', (b'hyadfadf')),
))
def test_comment_with_invalid_comment(client, auth, comment, messages):
    # Login a user.
    auth.login()

    # Attempt to comment on an article.
    response = client.post(
        '/comment?id=2&title=Food',
        data={'rating': 3, 'comment': "this is good"}
    )
    # Check that supplying invalid comment text generates appropriate error messages.
    for message in messages:
        assert message in response.data

def test_browse_with_pageNumber(client):
    # Check that we can retrieve the articles page.
    response = client.get('/display_all_tracks?page_number=0')
    assert response.status_code == 200

    # Check that without providing a date query parameter the page includes the first article.
    assert b'Food' in response.data
    assert b'Track ID: 2' in response.data

def test_browse_without_pageNumber(client):
    # Check that we can retrieve the articles page.
    response = client.get('/display_all_tracks')
    assert response.status_code == 200

    # Check that without providing a date query parameter the page includes the first article.
    assert b'Food' in response.data
    assert b'Track ID: 2' in response.data




def test_favourites(client):
    # Test that we can retrieve the favorites page
    response = client.get('/favorites')
    assert response.status_code == 200


def test_title_search(client):
    # Testing that search function retrieves the title of tracks even without full title
    response = client.post('/search',
                           data={'search': 'light'})
    assert response.status_code == 200
    assert b'Light of Light' in response.data
    assert b'Cloud Light' in response.data
    assert b'Starlight' in response.data
    assert b'Lights on Einstein' in response.data


def test_genre_search(client):
    # Testing that genre search works when full genre name is entered
    response = client.post('/search',
                           data={'search': 'hip-hop'})
    assert response.status_code == 200
    assert b'Food' in response.data
    assert b'Electric Ave' in response.data
    assert b'This World' in response.data


def test_artist_search(client):
    # Testing that artist search works when full artist name is entered
    response = client.post('/search',
                           data={'search': 'awol'})
    assert response.status_code == 200
    assert b'Food' in response.data
    assert b'Electric Ave' in response.data
    assert b'Street Music' in response.data


def test_add_favorites_no_login(client):
    # Tests to see what happens when a guest tries to add track to favorites
    response = client.get('added?track=<Track+Food,+track+id+%3D+2>')
    assert b'You need to be logged in to see your favorites!' in response.data


def test_add_favorites_with_login(client, auth):
    # Tests that favorites can be added from a logged-in user
    auth.login()
    response = client.get('added?track=<Track+Food,+track+id+%3D+2>')
    assert b'Food has been added to your favourites!' in response.data


def test_remove_favorites(client, auth):
    # Tests that favourites can be removed from logged-in user after they are added
    auth.login()
    client.get('added?track=<Track+Food,+track+id+%3D+2>')
    response = client.get('removed?track=<Track+Food,+track+id+%3D+2>')
    assert b"Food has been removed from your favourites!" in response.data


def test_login_search(client, auth):
    # Tests that search can be used by logged-in users
    auth.login()
    response = client.post('/search',
                           data={'search': 'light'})
    assert response.status_code == 200
    assert b'Light of Light' in response.data
    assert b'Cloud Light' in response.data
    assert b'Starlight' in response.data
    assert b'Lights on Einstein' in response.data
