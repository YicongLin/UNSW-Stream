import pytest
import requests
import json
from src import config
from datetime import datetime, timezone
import math

BASE_URL = 'http://127.0.0.1:7777'

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
    # first user tries to make a search
    payload = {
        "token": token,
        "query_str": "I am invalid"
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload)
    assert r.status_code == 403

# Testing for invalid query_str length
def test_invalid_query_str_length(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user tries to make a search with an empty query_str
    payload1 = {
        "token": token,
        "query_str": ""
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload1)
    assert r.status_code == 400
    # first user tries to make a search with a query_str with over 1000 characters
    payload2 = {
        "token": token,
        "query_str": "Lorem ipsum dolor sit amet, \
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
    r = requests.get(f'{BASE_URL}/search/v1', params = payload2)
    assert r.status_code == 400

# Testing for a valid case where there is a match to the search
def test_search_found(clear_setup, register_first, register_second, channel_one, channel_two, dm_one, dm_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id_1 = register_first['auth_user_id']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user creates channel
    channel_two
    # first user creates a DM with second user
    dm_one
    # second user creates a DM with first and third users; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user joins first channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi everyone, nice to meet you"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # obtaining the time the message is created
    time = datetime.now()
    time_created1 = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user sends a message to the DM
    payload3 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi everyone, this is a DM"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload3)
    # obtaining the time the message is created
    time = datetime.now()
    time_created2 = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # second user makes a valid search
    payload4 = {
        "token": token_2,
        "query_str": "Hi everyone"
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload4)
    assert r.status_code == 200
    message1 = {
        "message_id": 1,
        "u_id": u_id_1,
        "message": "Hi everyone, nice to meet you",
        "time_created": time_created1
    }
    message2 = {
        "message_id": 2,
        "u_id": u_id_1,
        "message": "Hi everyone, this is a DM",
        "time_created": time_created2
    }
    response = r.json()
    assert response == {"messages": [message1, message2]}

# Testing for a valid case where there is no match to the search
def test_search_not_found(clear_setup, register_first, register_second, channel_one, dm_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user creates a DM with first and third users; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user joins first channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi everyone, nice to meet you"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user sends a message to the DM
    payload3 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi everyone, this is a DM"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload3)
    # second user makes a search
    payload4 = {
        "token": token_2,
        "query_str": "Hello"
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload4)
    response = r.json()    
    assert response == {"messages": []}

# Testing for a valid case where there are some matches to the search
def test_search_combination(clear_setup, register_first, register_second, channel_one, dm_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id_1 = register_first['auth_user_id']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user creates a DM with first and third users; obtain dm_id
    dm_id = dm_two['dm_id']
    # second user joins first channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi everyone"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    # first user sends a message to the DM
    payload3 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi guys"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload3)
    # second user makes a search
    payload4 = {
        "token": token_2,
        "query_str": "guys"
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload4)
    message = {
        "message_id": 2,
        "u_id": u_id_1,
        "message": "Hi guys",
        "time_created": time_created
    }
    response = r.json()    
    assert response == {"messages": [message]}

# Testing for a valid case where there are authorised user isn't a member of the channels/DMs
# that the matched messages are in
def test_not_a_member(clear_setup, register_first, register_third, channel_one, dm_one):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    # third user registers; obtain token and u_id
    token_3 = register_third['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Good morning"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)
    # first user sends a message to the DM
    payload2 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Goodnight"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload2)
    # third user makes a search
    payload3 = {
        "token": token_3,
        "query_str": "Good"
    }
    r = requests.get(f'{BASE_URL}/search/v1', params = payload3)
    response = r.json()    
    assert response == {"messages": []}











