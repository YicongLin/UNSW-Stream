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

# Second user creates a channel
@pytest.fixture
def create_channel(registered_second):
    token = registered_second['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with first user
@pytest.fixture
def create_dm(registered_first, registered_second):
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
def test_invalid_message_id(setup_clear, registered_second, create_channel):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # second user attempts to remove a message with an invalid message_id
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message_id": 1,
        "start": 0
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 400 

# Testing for a case where the authorised user did not send the original message,
# and doesn't have owner permissions in the DM
def test_no_user_permission(setup_clear, registered_first, registered_second, create_dm):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    # second user sends a message to the DM
    payload1 = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # first user attempts to remove the message
    payload2 = {
        "token": token_1,
        "message_id": 1,
        "start": 0
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    assert r.status_code == 403

# Testing for a valid case where the authorised user has owner permissions
# but wasn't the one to send the message
def test_owner_permission(setup_clear, registered_first, registered_second, create_dm):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user removes the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "start": 0
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    assert r.status_code == 200 

# Testing for a valid case where the authorised user sent the message
# but isn't an owner of the channel
def test_not_owner_valid(setup_clear, registered_first, create_channel):
    # first user registers; obtain token
    token = registered_first['token']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user joins channel
    payload1 = {
        "token": token,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user removes the message
    payload3 = {
        "token": token,
        "message_id": 1,
        "start": 0
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload3)
    assert r.status_code == 200 

# Test for a successful removal
def test_successful_removal(setup_clear, registered_second, create_channel):
    # second user registers; obtain token and u_id
    token = registered_second['token']
    u_id = registered_second['auth_user_id']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # second user sends a message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # second user removes the message
    payload2 = {
        "token": token,
        "message_id": 1,
        "start": 0
    }
    requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    # second user calls channel messages;
    # test that the original message is changed
    payload3 = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload3)
    message = {
        'message_id': 1,
        'u_id': u_id,
        'message': 'Bye',
        'time_created': time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}

