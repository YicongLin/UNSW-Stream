import pytest
import requests
import json
from src import config
import math
from src.auth import auth_register_v2
from src.dm import dm_create_v1
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

# First user creates a public dm
@pytest.fixture
def create_dm(registered_first, registered_second):
    token = registered_second['token']
    u_id_1 = registered_first['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id_1]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp


# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid dm ID
def test_invalid_dm(setup_clear, registered_first):
    # first user registers; obtain token
    token = registered_first['token']
    # first user request messages of a dm with invalid ID 
    payload2 = {
        "token": token,
        "dm_id": 5,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload2)
    assert r.status_code == 400

# Testing for a case where start is greater 
# than the total number of messages in the dm
def test_start_greater(setup_clear, registered_first, create_dm):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates dm; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user requests dm messages with an invalid start number
    payload2 = {
        "token": token,
        "dm_id": dm_id,
        "start": 2
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload2)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(setup_clear, registered_first, create_dm):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates dms; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to request dm messages
    payload = {
        "token": token,
        "dm_id": int(dm_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    assert r.status_code == 403

# Testing for a case where the user is not a member of the dm
def test_not_a_member(setup_clear, registered_first, create_dm):
    # first user registers; obtain token
    token = registered_first['token']
    # second user creates dm; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user attempts to request dm messages
    payload = {
        "token": token,
        "dm_id": int(dm_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    assert r.status_code == 403

def test_valid(setup_clear, registered_first, create_dm):
    # first user registers; obtain token and u_id
    token = registered_first['token']
    u_id = registered_first['auth_user_id']
    # first user creates dm; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user sends message to dm
    payload1 = {
        "token": token,
        "dm_id": int(dm_id),
        "message": "Goodnight"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp())
    # first user requests dm messages
    payload2 = {
        "token": token,
        "dm_id": int(dm_id),
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload2)
    assert r.status_code == 200
    message = {
        "message_id": 1,
        "u_id": u_id,
        "message": "Goodnight",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}
