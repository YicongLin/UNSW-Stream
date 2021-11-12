import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT
from datetime import datetime, timezone
from src.config import url

BASE_URL = url

# ==================================
# Test both start and active
# ==================================

def test_start_active():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # Possible time for running routes
    length = 10 # Assume start standup in 10 secs
    now_time = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    possible_time = [int(now_time + length), int(now_time + length + 1), int(now_time + length + 2)]

    # user_two ----> channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})

    # Login in user_two to create channel 
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # Implement active -----> successful implement
    # No standup is running
    resp = requests.get(f'{BASE_URL}/standup/active/v1', params={"token": token_2, "channel_id": channel_id})
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) =={'is_active': False, 'time_finish': None})

    # Start a standup in 10 secs -----> successful implement
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": channel_id, "length": length})
    assert (resp.status_code == 200)

    # Implement active -----> successful implement
    resp = requests.get(f'{BASE_URL}/standup/active/v1', params={"token": token_2, "channel_id": channel_id})
    assert (resp.status_code == 200)
    assert (json.loads(resp.text)['is_active'] == True)
    assert (json.loads(resp.text)['time_finish'] in possible_time)
    
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

def test_start_active_errors():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    
    # user_two ----> channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})

    # Login in user_two to create channel 
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # Implement start with a invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": 123123, "length": -10})
    assert (resp.status_code == 400)

    # Implement start with a negative integer as length (InputError 400)
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": channel_id, "length": -10})
    assert (resp.status_code == 400)

    # Start a standup in 10 secs -----> successful implement
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": channel_id, "length": 10})
    assert (resp.status_code == 200)

    # Implement start but there is one standup is running (InputError 400)
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": channel_id, "length": 10})
    assert (resp.status_code == 400)

    # Implement active with a invalid channel_id (InputError 400)
    resp = requests.get(f'{BASE_URL}/standup/active/v1', params={"token": token_2, "channel_id": 123123})
    assert (resp.status_code == 400)

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # User with invalid token to start standup (AccessError 403)
    # token_2 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_2, "channel_id": channel_id, "length": 10})
    assert (resp.status_code == 403)

    # User with invalid token to test standup active (AccessError 403)
    # token_2 is invalid already (same token formation)
    resp = requests.get(f'{BASE_URL}/standup/active/v1', params={"token": token_2, "channel_id": channel_id})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================   

    # Login user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Implement start but authorised user is not a member of channel (InputError 400)
    resp = requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token_1, "channel_id": channel_id, "length": 10})
    assert (resp.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
