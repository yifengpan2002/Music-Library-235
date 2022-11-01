from werkzeug.security import generate_password_hash, check_password_hash

from music.adapters.repository import AbstractRepository
from music.domainmodel.user import User

class NameNotUniqueException(Exception):
    pass

class UnknownUserException(Exception):
    pass

class AuthenticationException(Exception):
    pass

def get_user(username:str, repo:AbstractRepository):
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException
    else:
        user_dict = {'user_name': user.user_name,'password': user.password}
        return user_dict


def add_user(username:str, password :str, repo:AbstractRepository):#here we need to call the method in mem_repo
    user = repo.get_user(username)
    if user is None:#mean we dont have that use so we can add
        password_hash = generate_password_hash(password)
        user_id = len(repo.get_all_users())
        new_user = User(user_id, username, password_hash)
        repo.add_user(new_user)
    else:
        raise NameNotUniqueException

def validate_user(username:str , password:str, repo:AbstractRepository):
    authentication_state = False
    user = repo.get_user(username)
    if user is not None:
        authentication_state = check_password_hash(user.password, password)
    else:
        raise UnknownUserException
    if not authentication_state:
        raise AuthenticationException