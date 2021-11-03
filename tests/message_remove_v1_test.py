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
        "name": "1",
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
    # second user attempts to remove a message with an invalid message_id
    payload = {
        "token": token,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 400 

# Testing for a case where the authorised user did not send the original message,
# and doesn't have owner permissions in the DM
def test_no_user_permission(setup_clear, registered_first, registered_second, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
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
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    assert r.status_code == 403

# Testing for a valid case where the authorised user has owner permissions
# but wasn't the one to send the message
def test_owner_permission(setup_clear, registered_first, registered_second, dm_two):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Ok"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user removes the message
    payload2 = {
        "token": token_2,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    assert r.status_code == 200 

# Testing for a valid case where the authorised user sent the message
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
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user removes the message
    payload3 = {
        "token": token,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload3)
    assert r.status_code == 200 
    

# Test for a successful removal in a channel
def test_successful_removal_channel(setup_clear, registered_second, channel_one, channel_two, dm_one):
    # second user registers; obtain token and u_id
    token = registered_second['token']
    u_id = registered_second['auth_user_id']
    # first user creates dm and channel
    channel_one
    dm_one
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user sends a message to the channel
    payload = {
        "token": token,
        "u_id": u_id,
        "channel_id": channel_id,
        "message": "Yo"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # second user sends another message to the channel
    payload1 = {
        "token": token,
        "u_id": u_id,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user removes both messages
    payload2 = {
        "token": token,
        "message_id": 1
    }
    requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    payload3 = {
        "token": token,
        "message_id": 2
    }
    requests.delete(f'{BASE_URL}/message/remove/v1', json = payload3)
    # second user calls channel messages;
    # test that the original message is changed
    payload4 = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload4)
    response = r.json()
    assert response == {"messages": [], "start": 0, "end": -1}

# Testing for a successful removal in a DM
def test_successful_removal_dm(setup_clear, registered_second, dm_one, dm_two, channel_one):
    # second user registers; obtain token and u_id
    token = registered_second['token']
    u_id = registered_second['auth_user_id']
    # first user creates channel and DM
    channel_one
    dm_one
    # second user creates dm with first user; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the dm
    payload = {
        "token": token,
        "dm_id": dm_id,
        "message": "Yo"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # second user sends another message to the dm
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user removes both messages
    payload2 = {
        "token": token,
        "message_id": 1
    }
    requests.delete(f'{BASE_URL}/message/remove/v1', json = payload2)
    payload3 = {
        "token": token,
        "message_id": 2
    }
    requests.delete(f'{BASE_URL}/message/remove/v1', json = payload3)
    # second user calls DM messages;
    # test that the message is deleted
    payload4 = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload4)
    response = r.json()
    assert response == {"messages": [], "start": 0, "end": -1}

