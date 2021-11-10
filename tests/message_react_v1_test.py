import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone

BASE_URL = 'http://127.0.0.1:2000'

# ================================================
# ================= FIXTURES =====================
# ================================================

# Clear data store
@pytest.fixture
def setup_clear():
    requests.delete(f'{BASE_URL}/clear/v1')

# Register first user
@pytest.fixture
def registered_first():
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
def registered_second():
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# First user creates a channel
@pytest.fixture
def channel_one(registered_first):
    token = registered_first['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a channel
@pytest.fixture
def channel_two(registered_second):
    token = registered_second['token']
    payload = {
        "token": token,
        "name": "2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# First user creates a DM
@pytest.fixture
def dm_one(registered_first):
    token = registered_first['token']
    payload = {
        "token": token,
        "u_ids": []
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with first user
@pytest.fixture
def dm_two(registered_first, registered_second):
    token = registered_second['token']
    u_id = registered_first['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp


# ================================================
# =================== TESTS ======================
# ================================================

# Testing for when message_id does not refer to a valid message 
def test_invalid_message_id(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user attempts to edit a message with an invalid message_id
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message_id": 1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    assert r.status_code == 400 

# Testing for when react_id does not refer to a valid react ID
def test_invalid_react_id(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user attempts to edit a message with an invalid message_id
    payload = {
        "token": token,
        "channel_id": channel_id,
        "react_id": 2,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    assert r.status_code == 400 

# Testing for when the message already contains a react_id
def test_present_react_id()

    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    assert r.status_code == 400

# Testing for when there is a successful react in a channel
def test_successful_react_channel()

    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    assert r.status_code == 200

# Testing for when there is a successful react in a channel
def test_successful_react_dm()

    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    assert r.status_code == 200