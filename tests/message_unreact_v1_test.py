import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone
from src.config import url

BASE_URL = url

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

# Testing for invalid token
def test_invalid_token(setup_clear, registered_first):
    # first user registers; obtain token
    token = registered_first['token']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to unreact to a message
    payload = {
        "token": token,
        "message_id": 7,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload)
    assert r.status_code == 403

# Testing for when message_id does not refer to a valid message 
def test_invalid_message_id(setup_clear, registered_second):
    # second user registers; obtain token
    token = registered_second['token']
    # second user attempts to unreact to a message with an invalid message_id
    payload = {
        "token": token,
        "message_id": 7,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload)
    assert r.status_code == 400 

# Testing for when react_id does not refer to a valid react ID
def test_invalid_react_id(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user sends a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # second user reacts to the message 
    payload = {
        "token": token,
        "message_id": 1,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload)
    # second user attempts to unreact to the message with an invalid react_id
    payload = {
        "token": token,
        "message_id": 1,
        "react_id": 2
    }
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload)
    assert r.status_code == 400 

# Testing for a case where the message in a channel does not contain a react from the authorised user
def test_already_reacted_channel(setup_clear, registered_first, channel_one):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user sends a message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # first user attempts to unreact to the message
    payload2 = {
        "token": token,
        "message_id": 1,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the message in a DM does not contain a react from the authorised user
def test_already_reacted_dm(setup_clear, registered_first, dm_one):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates DM; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # first user attempts to unreact to the message
    payload2 = {
        "token": token,
        "message_id": 1,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload2)
    assert r.status_code == 400

# Testing for a successful unreact in a channel
def test_successful_unreact_channel(setup_clear, registered_first, registered_second, channel_one, channel_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token and u_id
    token_2 = registered_second['token']
    u_id_2 = registered_second['auth_user_id']
    # first user creates channel
    channel_one
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user joins second channel
    payload = {
        "token": token_1,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # second user sends a message to the channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # obtaining the time the message is sent
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # second user reacts to the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload2)
    # second user unreacts to the message
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload2)
    assert r.status_code == 200
    # second user requests channel messages; the list of u_ids should be empty,
    # 'is_this_user_reacted' should be 'False'
    payload3 = {
        "token": token_2,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload3)
    message = {
        'message_id': 1,
        'u_id': u_id_2,
        'message': 'Hi',
        'time_created': time_created,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}
    
# Testing for a successful unreact in a channel
def test_successful_unreact_dm(setup_clear, registered_second, dm_one, dm_two):
    # second user registers; obtain token and u_id
    token_2 = registered_second['token']
    u_id_2 = registered_second['auth_user_id']
    # first user creates DM
    dm_one
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the DM
    payload = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "Hi",
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # obtaining the time the message is sent
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # second user reacts to the message
    payload1 = {
        "token": token_2,
        "message_id": 1,
        "react_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/react/v1', json = payload1)
    # second user unreacts to the message
    r = requests.post(f'{BASE_URL}/message/unreact/v1', json = payload1)
    assert r.status_code == 200    
    # second user requests DM messages; the list of u_ids should be empty,
    # 'is_this_user_reacted' should be 'False'
    payload3 = {
        "token": token_2,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload3)
    message = {
        'message_id': 1,
        'u_id': u_id_2,
        'message': 'Hi',
        'time_created': time_created,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}
    
