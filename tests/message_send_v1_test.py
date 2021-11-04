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

# First user creates a public channel 
@pytest.fixture
def create_channel(registered_first):
    token = registered_first['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

<<<<<<< HEAD
=======

>>>>>>> master
# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid dm_id
def test_invalid_dm_id(setup_clear, registered_first):
    # first user registers; obtain token
    token = registered_first['token']
    # first user attempts to send a message to a channel with an invalid ID
    payload = {
        "token": token,
        "channel_id": 77,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token_id
def test_invalid_token_id(setup_clear, registered_first, create_channel):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to send a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 403

# Testing for invalid message length
def test_invalid_message_length(setup_clear, registered_first, create_channel):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user sends an empty message to the channel
    payload1 = {
        "token": token,
        "channel_id": channel_id,
        "message": ""
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    assert r.status_code == 400
    # first user sends a message with over 1000 characters to the channel
    payload2 = {
       "token": token,
        "channel_id": channel_id,
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
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the authorised user isn't a member of the channel
def test_not_a_member(setup_clear, registered_second, create_channel):
    # second user registers; obtain token
    token = registered_second['token']
    # first user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # second user attempts to send a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "I'm an imposter"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 403

# Testing all valid cases
def test_valid(setup_clear, registered_first, create_channel):
    # first user registers; obtain token
    token = registered_first['token']
    # first user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user sends a message
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

# Testing to ensure the message was sent to the specified channel
def test_sent_messages(setup_clear, registered_first, create_channel):
    # first user registers; obtain token and u_id
    token = registered_first['token']
    u_id = registered_first['auth_user_id']
    # first user creates channel; obtain channel_id
    channel_id = create_channel['channel_id']
    # first user sends a message to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user returns messages in the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    message = {
        "message_id": 1,
        "u_id": u_id,
        "message": "Hello World",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": -1}
