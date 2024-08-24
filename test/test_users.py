from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status


# Override dependency functions to ensure testing environment and session database is used
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


# Test return user
def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'codingwithrobytest'
    assert response.json()['email'] == 'codingwithroby@email.com'
    assert response.json()['first_name'] == 'Eric'
    assert response.json()['last_name'] == 'Roby'
    assert response.json()['role'] == 'Admin'
    assert response.json()['phone_number'] == '111 111 1111'


# Test changing user password successfully
def test_change_password_success(test_user):
    response = client.put("/user/password", json = {"password": "testpassword", 
                                                    "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Test unsuccessfully chaning user password
def test_change_password_fail(test_user):
    response = client.put("/user/password", json = {"password": "wrong_password", 
                                                    "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change.'}


# Test chaning phone number
def test_change_phonenumber_success(test_user):
    response = client.put("/user/phonenumber/2222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT