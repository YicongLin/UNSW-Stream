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
    # first user gets notifications
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token})
    # this should raise an error message of "Invalid token"
    assert r.status_code == 403

# Testing for invalid message length
def test_invalid_message_length(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user sends a message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user attempts to replace existing message 
    # with a new message greater than 1000 characters
    payload2 = {
        "token": token,
        "message_id": 1,
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
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the new message is an empty string
def test_empty_string_channel(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user sends a message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user replaces existing message with an empty message
    payload2 = {
        "token": token,
        "message_id": 1,
        "message": "" 
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
    # test that the message is now deleted;
    # second user requests channel messages
    payload3 = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload3)
    response = r.json()
    assert response == {"messages": [], "start": 0, "end": -1}

# Testing for a case where the new message is an empty string
def test_empty_string_dm(setup_clear, registered_second, dm_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates DM; obtain channel_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the DM
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user replaces existing message with an empty message
    payload2 = {
        "token": token,
        "message_id": 1,
        "message": "" 
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
    # test that the message is now deleted;
    # second user requests dm messages
    payload3 = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload3)
    response = r.json()
    assert response == {"messages": [], "start": 0, "end": -1}


# Testing for when message_id does not refer to a valid message 
def test_invalid_message_id(setup_clear, registered_second, channel_two):
    # second user registers; obtain token
    token = registered_second['token']
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # second user attempts to edit a message with an invalid message_id
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message_id": 1,
        "message": "Hello World"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload)
    assert r.status_code == 400 

# Testing for a case where the authorised user did not send the original message,
# and doesn't have owner permissions in the DM
def test_no_user_permission_dm(setup_clear, registered_first, registered_second, dm_two):
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
    # first user attempts to edit the message
    payload2 = {
        "token": token_1,
        "message_id": 1,
        "message": "Bye"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
    assert r.status_code == 403

# Testing for a case where the authorised user did not send the original message,
# and doesn't have owner permissions in the channel
def test_no_user_permission_channel(setup_clear, registered_first, registered_second, channel_one, dm_two):
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
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user joins channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # second user attempts to edit the message
    payload3 = {
        "token": token_2,
        "message_id": 2,
        "message": "Bye"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload3)
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
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user edits the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Bye"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
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
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # second user edits the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "message": "Bye"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
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
    # first user edits the message
    payload3 = {
        "token": token,
        "message_id": 1,
        "message": "Bye"
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload3)
    assert r.status_code == 200 

# Testing for a successful edit in a channel
def test_successful_edit_channel(setup_clear, registered_second, channel_one, channel_two):
    # second user registers; obtain token and u_id
    token = registered_second['token']
    u_id = registered_second['auth_user_id']
    # first user creates channel
    channel_one
    # second user creates channel; obtain channel_id
    channel_id = channel_two['channel_id']
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
    # second user edits the message
    payload2 = {
        "token": token,
        "message_id": 1,
        "message": "Bye"
    }
    requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
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

# Testing for a successful edit in a DM
def test_successful_edit_dm(setup_clear, registered_second, dm_one, dm_two):
    # second user registers; obtain token and u_id
    token = registered_second['token']
    u_id = registered_second['auth_user_id']
    # first user creates dm
    dm_one
    # second user creates dm with first user; obtain channel_id
    dm_id = dm_two['dm_id']
    # second user sends a message to the DM
    payload1 = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # second user edits the message
    payload2 = {
        "token": token,
        "message_id": 1,
        "message": "Bye"
    }
    requests.put(f'{BASE_URL}/message/edit/v1', json = payload2)
    # second user calls DM messages;
    # test that the original message is changed
    payload3 = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload3)
    message = {
        'message_id': 1,
        'u_id': u_id,
        'message': 'Bye',
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

