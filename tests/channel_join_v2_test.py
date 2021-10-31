import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone

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

# First user creates a private channel
@pytest.fixture
def channel_one(register_first):
    token = register_first['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": False
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a public channel
@pytest.fixture
def channel_two(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "2",
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
    # first user attempts to join a channel with invalid ID 
    payload = {
        "token": token,
        "channel_id": 5
    }
    r = requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(clear_setup, register_first, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to join channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    assert r.status_code == 403
        
# Testing for a case where the user is already a member
def test_already_a_member(clear_setup, register_first, channel_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user attempts to join channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    assert r.status_code == 400

# Testing for a case where the user is not a member of the valid private channel,
# nor are they a global owner
def test_private_and_not_global_owner(clear_setup, register_first, register_second, channel_one):
    # first user registers
    register_first
    # second user registers; obtain token
    token = register_second['token']
    # first user creates private channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user attempts to join channel
    payload = {
        "token": token,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    assert r.status_code == 403

def test_valid(clear_setup, register_first, register_second, channel_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    id_1 = register_first['auth_user_id']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    id_2 = register_second['auth_user_id']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user joins channel
    payload = {
        "token": token_1,
        "channel_id": channel_id
    }
    r = requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    assert r.status_code == 200
    # test that the user joined successfully;
    # first user requests channel details,
    # which should return a list of members including the first user
    r = requests.get(f'{BASE_URL}/channel/details/v2', params = payload)
    member1 = {
        "u_id": id_1,
        "email": "first@email.com",
        "name_first": "first",
        "name_last": "user",
        "handle_str": "firstuser"
    }
    member2 = {
        "u_id": id_2,
        "email": "second@email.com",
        "name_first": "second",
        "name_last": "user",
        "handle_str": "seconduser"
    }
    response = r.json()
    assert response == {"name": "2", "is_public": True, "owner_members": [member2], "all_members": [member2, member1]}




