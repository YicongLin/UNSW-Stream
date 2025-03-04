import pytest
import requests
import json
from src import config
import jwt
from src.token_helpers import decode_JWT
import math
from datetime import datetime, timezone
from src.config import url

BASE_URL = url

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

# Register third user
@pytest.fixture
def register_third():
    payload = {
        "email": "third@email.com", 
        "password": "password", 
        "name_first": "third", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with first user
@pytest.fixture
def create_dm(register_second, register_first):
    token = register_second['token']
    u_id = register_first['auth_user_id']
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

# Testing for invalid dm_id
def test_invalid_dm_id(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user attempts to send a message to a DM with an invalid ID
    payload = {
        "token": token,
        "dm_id": 77,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token_id
def test_invalid_token_id(clear_setup, register_first, create_dm):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to send a message to the DM
    payload = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 403

# Testing for invalid message length
def test_invalid_message_length(clear_setup, register_first, create_dm):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": ""
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    assert r.status_code == 400

    payload2 = {
       "token": token,
        "dm_id": dm_id,
        "message": "Lorem ipsum dolor sit amet, \
                    consectetuer adipiscing elit. Aenean commodo \
                    ligula eget dolor. Aenean massa. Cum sociis \
                    natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. \
                    Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat \
                    massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. \
                    In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu \
                    pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. \
                    Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, \
                    eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus.\
                    Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. \
                    Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. \
                    Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, \
                    sit amet adipiscing sem neque sed ipsum. No" 
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the authorised user isn't a member of the DM
def test_not_a_member(clear_setup, register_third, create_dm):
    # third user registers; obtain token
    token = register_third['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    payload = {
        "token": token,
        "dm_id": dm_id,
        "message": "I'm an imposter"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 403

# Testing all valid cases
def test_valid(clear_setup, register_first, create_dm):
    # first user registers; obtain token
    token = register_first['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']
    payload = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

# Testing to ensure the message was sent to the specified DM
def test_sent_messages(clear_setup, register_first, register_second, create_dm):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id_1 = register_first['auth_user_id']
    # second user registers; obtain token
    token_2 = register_second['token']
    # second user creates DM with first user; obtain dm_id
    dm_id = create_dm['dm_id']

    # first user sends a message to the DM
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # second user returns messages in the DM
    payload = {
        "token": token_2,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    message = {
        "message_id": 1,
        "u_id": u_id_1,
        "message": "Hello World",
        "time_created": time_created,
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


