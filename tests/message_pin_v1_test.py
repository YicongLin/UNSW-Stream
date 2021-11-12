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
    # second user attempts to pin a message with an invalid message_id
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message_id": 1,
        "message": "Hello World",
        "is_pinned": True
    }
    r = requests.post(f'{BASE_URL}/message/pin/v1', json = payload)
    assert r.status_code == 400 

# Testing for a case where the authorised user did not send the original message,
# and doesn't have owner permissions in the channel
def test_no_user_permission_channel(setup_clear, registered_first, registered_second, channel_two, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # second user creates DM with first user, obtain dm_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the dm
    payload = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user joins channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # second user sends a message to the channel
    payload2 = {
        "token": token_2,
        "channel_id": channel_id,
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user attempts to pin the message
    payload3 = {
        "token": token_1,
        "message_id": 2,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload3)
    assert r.status_code == 403

# Testing for a valid case where the authorised user has owner permissions in the DM
# but wasn't the one to send the message
def test_owner_permission_dm(setup_clear, registered_first, registered_second, dm_one, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # first user creates DM
    dm_one
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 200 

# Testing for a valid case where the authorised user has owner permissions in the channel
# but wasn't the one to send the message
def test_owner_permission_channel(setup_clear, registered_first, registered_second, channel_one, channel_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
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
    # first user sends a message to the channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 200 

# Testing for an invalid case where the authorised user sent the message
# but isn't an owner of the channel
def test_not_owner_valid(setup_clear, registered_first, channel_two):
    # first user registers; obtain token
    token = registered_first['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
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
        "message": "Hi",
        "is_pinned": False

    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user pins the message
    payload3 = {
        "token": token,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload3)
    assert r.status_code == 403

# Testing for when the message is already pinned in the channel
def test_message_already_pinned_channel(setup_clear, registered_first, registered_second, channel_one, channel_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
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
    # first user sends a message to the channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi",
        "is_pinned": True
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 400

def test_already_pinned_dm(setup_clear, registered_first, registered_second, dm_one, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # first user creates DM
    dm_one
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi",
        "is_pinned": True
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 400

# Testing for when there is a successful pin in a channel
def test_successful_pin_channel(setup_clear, registered_first, registered_second, channel_one, channel_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
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
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.post(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 200

# Testing for when there is a successful pin in a DM
def test_successful_pin_dm(setup_clear, registered_first, registered_second, dm_one, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # first user creates DM
    dm_one
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi",
        "is_pinned": False
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user pins the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Hi",
        "is_pinned": True
    }
    r = requests.put(f'{BASE_URL}/message/pin/v1', json = payload2)
    assert r.status_code == 200 