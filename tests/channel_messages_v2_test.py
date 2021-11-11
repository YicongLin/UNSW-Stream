import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone

BASE_URL = 'http://127.0.0.1:7777'

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

# First user creates a public channel
@pytest.fixture
def channel_one(register_first):
    token = register_first['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a private channel
@pytest.fixture
def channel_two(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "2",
        "is_public": False
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
    # first user request messages of a channel with invalid ID 
    payload2 = {
        "token": token,
        "channel_id": 5,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload2)
    assert r.status_code == 400

# Testing for a case where start is greater 
# than the total number of messages in the channel
def test_start_greater(clear_setup, register_first, channel_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user requests channel messages with an invalid start number
    payload2 = {
        "token": token,
        "channel_id": channel_id,
        "start": 2
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload2)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(clear_setup, register_first, channel_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to request channel messages
    payload = {
        "token": token,
        "channel_id": int(channel_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    assert r.status_code == 403

# Testing for a case where the user is not a member of the channel
def test_not_a_member(clear_setup, register_first, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user attempts to request channel messages
    payload = {
        "token": token,
        "channel_id": int(channel_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    assert r.status_code == 403

def test_valid(clear_setup, register_first, channel_one):
    # first user registers; obtain token and u_id
    token = register_first['token']
    u_id = register_first['auth_user_id']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user sends first message to channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Goodnight"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # obtaining the time the message is created
    time = datetime.now()
    time_created1 = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user sends second message to channel
    payload2 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Good morning"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # obtaining the time the message is created
    time = datetime.now()
    time_created2 = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user requests channel messages
    payload3 = {
        "token": token,
        "channel_id": int(channel_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload3)
    assert r.status_code == 200
    message1 = {
        "message_id": 1,
        "u_id": u_id,
        "message": "Goodnight",
        "time_created": time_created1
    }
    message2 = {
        "message_id": 2,
        "u_id": u_id,
        "message": "Good morning",
        "time_created": time_created2
    }
    response = r.json()
    assert response == {"messages": [message2, message1], "start": 0, "end": -1}
