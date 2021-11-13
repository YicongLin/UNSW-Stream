import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone
from src.config import url
from datetime import datetime, timezone
import math

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

# First user creates a DM with second user
@pytest.fixture
def dm_one(registered_first, registered_second):
    token = registered_first['token']
    u_id = registered_second['auth_user_id']
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
    # first user attempts to unpin a message
    payload = {
        "token": token,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload)
    assert r.status_code == 403

# Testing for when message_id does not refer to a valid message 
def test_invalid_message_id(setup_clear, registered_second):
    # second user registers; obtain token
    token = registered_second['token']
    # second user attempts to unpin a message with an invalid message_id
    payload = {
        "token": token,
        "message_id": 7
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload)
    assert r.status_code == 400 

# Testing for when the message is already unpinned in the channel
def test_message_already_unpinned_channel(setup_clear, registered_first, channel_one):
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
    # first user attempts to unpin the message
    payload2 = {
        "token": token,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload2)
    assert r.status_code == 400

# Testing for when the message is already unpinned in the DM
def test_message_already_unpinned_dm(setup_clear, registered_first, dm_one):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates DM; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi",
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # first user attempts to unpin the message
    payload2 = {
        "token": token,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the message ID is valid but the authorised user 
# doesn't have owner permissions in the channel
def test_no_owner_permissions_channel(setup_clear, registered_first, registered_second, channel_one):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user joins channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # second user sends a message to the channel
    payload2 = {
        "token": token_2,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user pins the message
    payload3 = {
        'token': token_1,
        'message_id': 1
    }
    requests.post(f'{BASE_URL}/message/pin/v1', json = payload3)
    # second user attempts to unpin the message
    payload4 = {
        "token": token_2,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload4)
    assert r.status_code == 403

# Testing for a case where the message ID is valid but the authorised user 
# doesn't have owner permissions in the DM
def test_no_owner_permissions_dm(setup_clear, registered_first, registered_second, dm_one):
    # first user registers; obtain token
    token_1 = registered_first['token']
    # second user registers; obtain token
    token_2 = registered_second['token']
    # first user creates DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # first user pins the message
    payload3 = {
        'token': token_1,
        'message_id': 1
    }
    requests.post(f'{BASE_URL}/message/pin/v1', json = payload3)
    # second user attempts to unpin the message
    payload4 = {
        "token": token_2,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload4)
    assert r.status_code == 403
   
# Testing for a successful unpin in a channel
def test_successful_unpin_channel(setup_clear, registered_first, channel_one):
    # first user registers; obtain token and u_id
    token = registered_first['token']
    u_id = registered_first['auth_user_id']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user sends a message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # obtaining the time the message is sent
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user pins the message
    payload2 = {
        'token': token,
        'message_id': 1
    }
    requests.post(f'{BASE_URL}/message/pin/v1', json = payload2)
    # first user unpins the message
    payload3 = {
        "token": token,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload3)
    assert r.status_code == 200
    # first user requests channel messages; the 'is_pinned' key should be False
    payload4 = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload4)
    message = {
        'message_id': 1,
        'u_id': u_id,
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

# Testing for a successful unpin in a DM
def test_successful_unpin_dm(setup_clear, registered_first, dm_one):
    # first user registers; obtain token and u_id
    token = registered_first['token']
    u_id = registered_first['auth_user_id']
    # first user creates DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # obtaining the time the message is sent
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user pins the message
    payload2 = {
        'token': token,
        'message_id': 1
    }
    requests.post(f'{BASE_URL}/message/pin/v1', json = payload2)
    # first user unpins the message
    payload3 = {
        "token": token,
        "message_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/unpin/v1', json = payload3)
    assert r.status_code == 200
    # first user requests DM messages; the 'is_pinned' key should be False
    payload4 = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload4)
    message = {
        'message_id': 1,
        'u_id': u_id,
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
