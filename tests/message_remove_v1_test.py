import pytest
import requests
import json
from src import config
import math
from src.auth import auth_register_v2
from src.dm import dm_create_v1
from src.channels import channels_create_v2
from src.token_helpers import decode_JWT
from src.other import clear_v1
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

# Register third user
@pytest.fixture
def registered_third():
    payload = {
        "email": "third@email.com", 
        "password": "password", 
        "name_first": "third", 
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

# Second user creates a DM with first and third users
@pytest.fixture
def create_dm(registered_first, registered_second, registered_third):
    token = registered_second['token']
    u_id_3 = registered_third['auth_user_id']
    u_id_1 = registered_first['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id_1, u_id_3]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp

# ================================================
# =================== TESTS ======================
# ================================================

# Testing if message_id does not refer to a valid message 
def test_invalid_message_id(setup_clear, registered_first):
     # first user registers; obtain token
    token = registered_first['token']
    # first user attempts to send a message with an invalid message_id
    payload = {
        "token": token,
        "message_id": 0
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 400 


# Testing for when the user making the request has invalid access
# the message was sent by the authorised user making this request
# and the authorised user has owner permissions in the channel/DM
def test_no_user_permission(setup_clear, registered_first, registered_second):
    # first user registers; obtain token and u_id
    token_1 = registered_first['token']
    u_id_1 = registered_first['auth_user_id']
    # second user registers; obtain token and u_id
    token_2 = registered_second['token']
    u_id_2 = registered_second['auth_user_id']
    # second user creates channel with first user
    dm_id = create_dm['dm_id']
    # first user sends a message to the dm
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message_id": message_id,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # obtaining the time the message is created
    time = datetime.now()
    time_created1 = math.floor(time.replace(tzinfo=timezone.utc).timestamp())
    # second user attempts to remove the message
    payload = {
        "token": token_2,
        "dm_id": dm_id,
        "message_id": message_id
        "message": " "
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 400 


# Testing for when the function fails to remove messages
def test_unremoved_message(setup_clear, registered_first, registered_second, registered_third):
    # first user registers; obtain token and u_id
    token_1 = registered_first['token']
    u_id_1 = registered_first['auth_user_id']
 # second user registers; obtain token and u_id
    token_2 = registered_second['token']
    u_id_2 = registered_second['auth_user_id']
    # third user registers; obtain u_id
    u_id_3 = registered_third['auth_user_id']
    # second user creates channel with first and third user; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user sends a message to the dm
    payload = {
        "token": token_1,
        "channel_id": channel_id,
        "message_id": message_id,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # obtaining the time the message is created
    time = datetime.now()
    time_created1 = math.floor(time.replace(tzinfo=timezone.utc).timestamp())

    payload = {
        "token": token,
        "channel_id": channel_id,
        "message_id": message_id
        "message": "Hello World"
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 400 

# Testing the function removes messages
def test_messages_removed(setup_clear, registered_first, registered_second, registered_third):
     # first user registers; obtain token and u_id
    token_1 = registered_first['token']
    u_id_1 = registered_first['auth_user_id']
 # second user registers; obtain token and u_id
    token_2 = registered_second['token']
    u_id_2 = registered_second['auth_user_id']
    # third user registers; obtain u_id
    u_id_3 = registered_third['auth_user_id']
    # second user creates DM with first and third user; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user sends a message to the dm
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message_id": message_id,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # obtaining the time the message is created
    time = datetime.now()
    time_created1 = math.floor(time.replace(tzinfo=timezone.utc).timestamp())

    payload = {
        "token": token
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 200
    