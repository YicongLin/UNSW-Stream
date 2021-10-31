import pytest
import requests
import json
from src import config
from datetime import datetime, timezone
import math

BASE_URL = 'http://127.0.0.1:3178'

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

# Second user creates a channel
@pytest.fixture
def create_channel(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with third user
@pytest.fixture
def create_dm(register_second, register_third):
    token = register_second['token']
    u_id = register_third['auth_user_id']
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

# Testing for invalid u_id
def test_invalid_u_id(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user attempts to remove a user with an invalid ID
    payload = {
        "token": token, 
        "u_id": "invalid_uid"
        }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    # this should raise an error message of "Invalid user"
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to remove the second user
    payload = {
        "token": token,
        "u_id": u_id
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    # this should raise an error message of "Invalid token"
    assert r.status_code == 403

# Testing for a case where u_id is the only global owner 
# and they are being removed
def test_global_owner_removed(clear_setup, register_first):
    # first user registers; obtain token and u_id
    token = register_first['token']
    u_id = register_first['auth_user_id']
    # first user attempts to remove themselves
    payload = {
        "token": token, 
        "u_id": u_id
        }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    # this should raise an error message of "Cannot remove the only global owner"
    assert r.status_code == 400 

# Testing for a case where the authorised user is not a global owner
def test_not_global_owner(clear_setup, register_first, register_second, register_third):
    # first user registers
    register_first
    # second user registers; obtain token 
    token = register_second['token']
    # third user registers; obtain u_id
    u_id = register_third['auth_user_id']
    # second user tries to remove third user 
    payload = {
        "token": token,
        "u_id": u_id
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    # this should raise an error message of "You are not a global owner"
    assert r.status_code == 403

# Test valid case
def test_valid(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user removes the second user 
    payload = {
        "token": token,
        "u_id": u_id
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 200

# Test user removal from channel members list, as well as removal of messages
def test_all_removed_from_channel(clear_setup, register_first, register_second, register_third, create_channel):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    u_id_2 = register_second['auth_user_id']
    # third user registers; obtain token
    token_3 = register_third['token']
    u_id_3 = register_third['auth_user_id']
    # second user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # third user joins channel
    payload1 = {
        "token": token_3,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # second user sends a message to the channel
    payload2 = {
        "token": token_2,
        "channel_id": channel_id,
        "message": "Bye"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp())
    
    # the second user is removed from Streams
    payload3 = {
        "token": token_1,
        "u_id": u_id_2
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload3)
    # test that the second user is removed from channel;
    # the third user requests channel details,
    # which should return a list that does not include the second user
    r = requests.get(f'{BASE_URL}/channel/details/v2', params = payload1)
    member = {
        "u_id": u_id_3,
        "email": "third@email.com",
        "name_first": "third",
        "name_last": "user",
        "handle_str": "thirduser"
    }
    assert r.status_code == 200
    response = r.json()
    assert response == {"name": "1", "is_public": True, "owner_members": [], "all_members": [member]}
    # test that the sent message is removed;
    # the third user requests channel messages which should return
    # a message replaced with "Removed user"
    payload4 = {
        "token": token_3,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload4)
    message = {
        "message_id": 1,
        "u_id": u_id_2,
        "message": "Removed user",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}

# Test user removal from dm members list, as well as removal of messages
def test_all_removed_from_dm(clear_setup, register_first, register_second, register_third, create_dm):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    u_id_2 = register_second['auth_user_id']
    # third user registers; obtain token
    token_3 = register_third['token']
    u_id_3 = register_third['auth_user_id']
    # second user creates DM with third user; obtain dm_id
    dm_id = create_dm['dm_id']
    # second user sends a message to the dm
    payload1 = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "Bye"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp())
    # second user is removed from Streams
    payload2 = {
        "token": token_1,
        "u_id": u_id_2
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload2)
    # test that the second user is removed from dm;
    # the third user requests channel details,
    # which should return a list that does not include the second user
    payload3 = {
        "token": token_3,
        "dm_id": dm_id
    }
    r = requests.get(f'{BASE_URL}/dm/details/v1', params = payload3)
    user = {
        "u_id": u_id_3,
        "email": "third@email.com",
        "name_first": "third",
        "name_last": "user",
        "handle_str": "thirduser"
    }
    response = r.json()
    assert response == {"name": ["thirduser"], "members": [user]}

    # assert the sent message is removed;
    # id_3 requests dm messages - the message will be replaced with "Removed user"
    payload4 = {
        "token": token_3,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload4)
    message = {
        "message_id": 1,
        "u_id": u_id_2,
        "message": "Removed user",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}

# Test user removal from user list, but still also retrievable with user/profile
def test_user_list_and_profile(clear_setup, register_first, register_second):
     # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id_1 = register_first['auth_user_id']
    # second user registers; obtain u_id
    u_id_2 = register_second['auth_user_id']

    # first user removes second and third users 
    payload1 = {
        "token": token_1,
        "u_id": u_id_2
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload1)
    # test that the second user is removed from users list;
    # first user requests user list
    r = requests.get(f'{BASE_URL}/users/all/v1', params = {"token": token_1})
    user = {
        "u_id": u_id_1,
        "email": "first@email.com",
        "name_first": "first",
        "name_last": "user",
        "handle_str": "firstuser"
    }
    response = r.json()
    assert response == {"users": [user]}
    # test that the second user should still be retrievable with user/profile;
    # first user requests second user's profile
    r = requests.get(f'{BASE_URL}/user/profile/v1', params = payload1)
    user = {
        "u_id": u_id_2,
        "email": '',
        "name_first": 'Removed',
        "name_last": 'user',
        "handle_str": ''
    }
    response = r.json()
    assert response == {"user": user}

