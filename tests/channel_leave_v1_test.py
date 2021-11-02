import pytest
import requests
import json
from src import config
BASE_URL = 'http://127.0.0.1:3210'

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

# Second user creates a channel
@pytest.fixture
def create_channel(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid channel ID
def test_invalid_channel(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    payload = {
        "token": token,
        "channel_id": "invalid_id"
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(clear_setup, register_second, create_channel):
    # second user registers; obtain token
    token = register_second['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # second user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # second user attempts to leave channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where the user is not a member of the channel
def test_not_a_member(clear_setup, register_first, create_channel):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user attempts to leave channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 403

# Testing valid case
def test_valid(clear_setup, register_second, create_channel):
    # second user registers; obtain token
    token = register_second['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # second user leaves channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 200

# Ensuring the user is gone from the list of channels after leaving
def test_user_left(clear_setup, register_first, register_second, create_channel):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    id_1 = register_first['auth_user_id']
    # second user registers; obtain token
    token_2 = register_second['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user joins the channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # second user leaves channel
    payload2 = {
        "token": token_2,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload2)
    # first user returns channel details
    r = requests.get(f'{BASE_URL}/channel/details/v2', params = payload1)
    member = {
        "u_id": id_1,
        "email": "first@email.com",
        "name_first": "first",
        "name_last": "user",
        "handle_str": "firstuser"
    }
    response = r.json()
    assert response == {"name": "1", "is_public": True, "owner_members": [], "all_members": [member]}
