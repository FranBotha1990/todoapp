from .utils import *
from ..routers.auth import get_db, authenticate_user
from fastapi import status


# Override dependency functions to ensure testing environment and session database is used
app.dependency_overrides[get_db] = override_get_db


# Test authenticating user, also wrong username or wrong password
def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False


