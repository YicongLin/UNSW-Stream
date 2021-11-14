import pytest
import requests
import json
from src import config
from datetime import datetime, timezone
import math
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

# First user creates a public channel
@pytest.fixture
def channel_one(register_first):
    token = register_first['token']
    payload = {
        "token": token,
        "name": "Channel one",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a public channel
@pytest.fixture
def channel_two(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "Channel two",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# First user creates a DM with second user
@pytest.fixture
def dm_one(register_first, register_second):
    token = register_first['token']
    u_id = register_second['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with first and third users
@pytest.fixture
def dm_two(register_first, register_second, register_third):
    token = register_second['token']
    u_id_1 = register_first['auth_user_id']
    u_id_3 = register_third['auth_user_id']
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

# Testing for invalid token
def test_invalid_token(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to share a message
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Hi",
        "channel_id": 1,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 403
    
# Testing for a case where both channel and DM IDs are invalid
def test_invalid_channel_dm_id(clear_setup, register_first, channel_one, dm_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user creates a DM; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user attempts to share a message with invalid channel_id
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Bye",
        "channel_id": 7,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 400
    # first user sends a message to the DM 
    payload = {
        "token": token,
        "dm_id": dm_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # first user attempts to share the message with invalid dm_id
    payload = {
        'token': token,
        'og_message_id': 2,
        'message': "Bye",
        "channel_id": -1,
        "dm_id": 7
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 400

# Testing for a case where neither channel nor DM IDs are -1
def test_both_ids_not_negative_one(clear_setup, register_first, channel_one, dm_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user creates a DM
    dm_one
    # first user sends a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user attempts to share the message with both channel and DM IDs not -1
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Bye",
        "channel_id": 1,
        "dm_id": 1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 400

# Testing for a case where og_message_id does not refer to a valid message 
# within a channel/DM that the authorised user has joined
def test_invalid_og_message_id(clear_setup, register_first, channel_one, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a channel; obtain channel_id
    channel_id_1 = channel_one['channel_id']
    # second user creates a channel; obtain channel_id
    channel_id_2 = channel_two['channel_id']
    # first user joins second channel
    payload = {
        "token": token,
        "channel_id": channel_id_2,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # first user sends a message to first channel
    payload = {
        "token": token,
        "channel_id": channel_id_1,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user attempts to share the message with an invalid message ID
    payload = {
        'token': token,
        'og_message_id': 7,
        'message': "Bye",
        "channel_id": channel_id_2,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 400

# Testing for when the message length is greater than 1000 characters
def test_invalid_message_length(clear_setup, register_first, channel_one, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a channel; obtain channel_id
    channel_id_1 = channel_one['channel_id']
    # second user creates a channel; obtain channel_id
    channel_id_2 = channel_two['channel_id']
    # first user joins second channel
    payload = {
        "token": token,
        "channel_id": channel_id_2,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # first user sends a message to first channel
    payload = {
        "token": token,
        "channel_id": channel_id_1,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user attempts to share the message with an additional message 
    # that has a length of greater than 1000 characters
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Lorem ipsum dolor sit amet, \
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
                    sit amet adipiscing sem neque sed ipsum. No",
        "channel_id": channel_id_2,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 400

# Testing for a case where the authorised user hasn't joined the channel 
# they are trying to share the message to 
def test_not_a_channel_member(clear_setup, register_first, channel_one, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a channel; obtain channel_id
    channel_id_1 = channel_one['channel_id']
    # second user creates a channel; obtain channel_id
    channel_id_2 = channel_two['channel_id']
    # first user sends a message to first channel
    payload = {
        "token": token,
        "channel_id": channel_id_1,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user attempts to share the message to second channel
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Bye",
        "channel_id": channel_id_2,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 403
 
# Testing for a case where the authorised user hasn't joined the DM 
# they are trying to share the message to 
def test_not_a_dm_member(clear_setup, register_first, dm_one, dm_two):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates a DM with second user; obtain dm_id
    dm_id_1 = dm_one['dm_id']
    # second user creates a DM with first and third users; obtain dm_id
    dm_id_2 = dm_two['dm_id']
    # first user leaves second DM
    payload = {
        'token': token,
        'dm_id': dm_id_2
    }
    requests.post(f'{BASE_URL}/dm/leave/v1', json = payload)
    # first user sends a message to first DM
    payload = {
        "token": token,
        "dm_id": dm_id_1,
        "message": "Hi"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # first user attempts to share the message to second DM
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "Bye",
        "channel_id": -1,
        "dm_id": dm_id_2
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where the message is successfully shared to a channel,
# with and without an additional message
def test_successful_share_channel(clear_setup, register_first, channel_one, channel_two):
    # first user registers; obtain token and u_id
    token = register_first['token']
    u_id = register_first['auth_user_id']
    # first user creates a channel; obtain channel_id
    channel_id_1 = channel_one['channel_id']
    # second user creates a channel; obtain channel_id
    channel_id_2 = channel_two['channel_id']
    # first user joins second channel
    payload = {
        "token": token,
        "channel_id": channel_id_2,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # first user sends a message to first channel
    payload = {
        "token": token,
        "channel_id": channel_id_1,
        "message": "This is the original message"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user shares the message to second channel with no additional message
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "",
        "channel_id": channel_id_2,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # obtaining the time the message is shared
    time = datetime.now()
    time_shared = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user shares the message to second channel with an additional message
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "This is the additional message",
        "channel_id": channel_id_2,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # test that the messages have been shared to the second channel; 
    # first user requests channel messages
    payload = {
        'token': token,
        'channel_id': channel_id_2,
        'start': 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    message1 = {
        'message_id': 2,
        'u_id': u_id,
        'message': "This is the original message",
        'time_created': time_shared,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    message2 = {
        'message_id': 3,
        'u_id': u_id,
        'message': "This is the original messageThis is the additional message",
        'time_created': time_shared,
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
    assert response == {'messages': [message2, message1], 'start': 0, 'end': -1}

# Testing for a case where the message is successfully shared to a DM,
# with and without an additional message
def test_successful_share_dm(clear_setup, register_first, dm_one, dm_two):
    # first user registers; obtain token and u_id
    token = register_first['token']
    u_id = register_first['auth_user_id']
    # first user creates a DM with second user; obtain dm_id
    dm_id_1 = dm_one['dm_id']
    # second user creates a DM with first and third users; obtain dm_id
    dm_id_2 = dm_two['dm_id']
    # first user sends a message to first DM
    payload = {
        "token": token,
        "dm_id": dm_id_1,
        "message": "This is the original message"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # first user shares the message to second DM with no additional message
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "",
        "channel_id": -1,
        "dm_id": dm_id_2
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # obtaining the time the message is shared
    time = datetime.now()
    time_shared = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user shares the message to second DM with an additional message
    payload = {
        'token': token,
        'og_message_id': 1,
        'message': "This is the additional message",
        "channel_id": -1,
        "dm_id": dm_id_2
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # test that the messages have been shared to the second DM; 
    # first user requests DM messages
    payload = {
        'token': token,
        'dm_id': dm_id_2,
        'start': 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    message1 = {
        'message_id': 2,
        'u_id': u_id,
        'message': "This is the original message",
        'time_created': time_shared,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    message2 = {
        'message_id': 3,
        'u_id': u_id,
        'message': "This is the original messageThis is the additional message",
        'time_created': time_shared,
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
    assert response == {'messages': [message2, message1], 'start': 0, 'end': -1}

# Testing for a case where a message is being shared to the same channel it was originally in, 
# and the additional message contains a tag; the tagged user should receive a notification
def test_additional_message_with_tags_channel(clear_setup, register_first, register_second, channel_one):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id = register_first['auth_user_id']
    # second user registers; obtain token
    token_2 = register_second['token']
    # first user creates a channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user joins the channel
    payload = {
        "token": token_2,
        "channel_id": channel_id,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # first user sends a message to the channel
    payload = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "This is the original message"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # first user shares the message to the channel with an additional message, tagging the second user
    payload = {
        'token': token_1,
        'og_message_id': 1,
        'message': "Look @seconduser",
        "channel_id": channel_id,
        "dm_id": -1
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # obtaining the time the message is shared
    time = datetime.now()
    time_shared = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # test that the message has been shared to the channel; 
    # first user requests channel messages
    payload = {
        'token': token_1,
        'channel_id': channel_id,
        'start': 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    message1 = {
        'message_id': 1,
        'u_id': u_id,
        'message': "This is the original message",
        'time_created': time_shared,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    message2 = {
        'message_id': 2,
        'u_id': u_id,
        'message': "This is the original messageLook @seconduser",
        'time_created': time_shared,
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
    assert response == {'messages': [message2, message1], 'start': 0, 'end': -1}
    # test that the second user receives a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    notification = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "firstuser tagged you in Channel one: Look @seconduser"
    }
    response = r.json()
    assert response == {"notifications": [notification]}

# Testing for a case where a message is being shared to the same DM it was originally in, 
# and the additional message contains a tag; the tagged user should receive a notification
def test_additional_message_with_tags_dm(clear_setup, register_first, register_second, dm_one):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id = register_first['auth_user_id']
    # second user registers; obtain token
    token_2 = register_second['token']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "This is the original message"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # first user shares the message to the DM with an additional message, tagging the second user
    payload = {
        'token': token_1,
        'og_message_id': 1,
        'message': "Look @seconduser",
        "channel_id": -1,
        "dm_id": dm_id
    }
    r = requests.post(f'{BASE_URL}/message/share/v1', json = payload)
    assert r.status_code == 200
    # obtaining the time the message is shared
    time = datetime.now()
    time_shared = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # test that the message has been shared to the DM; 
    # first user requests DM messages
    payload = {
        'token': token_1,
        'dm_id': dm_id,
        'start': 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    message1 = {
        'message_id': 1,
        'u_id': u_id,
        'message': "This is the original message",
        'time_created': time_shared,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }
    message2 = {
        'message_id': 2,
        'u_id': u_id,
        'message': "This is the original messageLook @seconduser",
        'time_created': time_shared,
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
    assert response == {'messages': [message2, message1], 'start': 0, 'end': -1}
    # test that the second user receives a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    notification1 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "firstuser added you to firstuser, seconduser"
    }
    notification2 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "firstuser tagged you in firstuser, seconduser: Look @seconduser"
    }
    response = r.json()
    assert response == {"notifications": [notification2, notification1]}