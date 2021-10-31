import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.other import clear_v1

BASE_URL = 'http://127.0.0.1:3178'

# ================================================
# ================= FIXTURES =====================
# ================================================

# Clear data store
@pytest.fixture
def clear_setup():
    requests.delete(f'{BASE_URL}/clear/v1')

# Register first user
@pytest.fixture
def register_first():
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# Register second user
@pytest.fixture
def register_second():
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# Register third user
@pytest.fixture
def register_third():
    payload = {
        "email": "third@email.com", 
        "password": "password", 
        "name_first": "third", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid u_id
def test_invalid_u_id(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user attempts to change permission ID of a user with an invalid ID
    payload = {
        "token": token, 
        "u_id": "invalid_uid", 
        "permission_id": 1
        }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    # this should raise an error message of "Invalid user"
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to change permission of the second user
    payload = {
        "token": token,
        "u_id": u_id,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    # this should raise an error message of "Invalid token"
    assert r.status_code == 403

    
# Testing for a case where u_id is the only global owner 
# and they are being demoted
def test_global_owner_demoted(clear_setup, register_first):
    # first user registers; obtain token and u_id
    token = register_first['token']
    u_id = register_first['auth_user_id']
    # first user attempts to demote themselves
    payload = {
        "token": token, 
        "u_id": u_id, 
        "permission_id": 2
        }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    # this should raise an error message of "Cannot demote the only global owner"
    assert r.status_code == 400 

# Testing for invalid permission_id
def test_invalid_permission_id(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user attempts to change permission of the second user with an invalid permission ID
    payload = {
        "token": token, 
        "u_id": u_id, 
        "permission_id": 3
        }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    # this should raise an error message of "Invalid permission ID"
    assert r.status_code == 400

# Testing for a case where the authorised user is not a global owner
def test_not_global_owner(clear_setup, register_first, register_second, register_third):
    # first user registers
    register_first
    # second user registers; obtain token 
    token = register_second['token']
    # third user registers; obtain u_id
    u_id = register_third['auth_user_id']
    # second user tries to promote third user 
    payload = {
        "token": token,
        "u_id": u_id,
        "permission_id": 2
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    # this should raise an error message of "You are not a global owner"
    assert r.status_code == 403

# Test valid case
def test_valid(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user changes permission of the second user 
    payload = {
        "token": token,
        "u_id": u_id,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 200

# Test that permission_id has been changed
def test_changed(clear_setup, register_first, register_second, register_third):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    u_id_2 = register_second['auth_user_id']
    # third user registers; obtain u_id
    u_id_3 = register_third['auth_user_id']
    # first user promotes second user to global owner
    payload1 = {
        "token": token_1,
        "u_id": u_id_2,
        "permission_id": 1
    }
    requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload1)
    # test that the second user's permissions have been changed;
    # the second user should now be able to promote the third user
    payload2 = {
        "token": token_2,
        "u_id": u_id_3,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload2)
    assert r.status_code == 200
 