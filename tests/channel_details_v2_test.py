import pytest
import requests
import json
from src import config

from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:1231'
 
# ==================================
# Test channel_details function
# ==================================
    
def test_channel_details():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # Register two users
    # user_one ----> channel creator (only member)
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    uid_1 = decode_JWT(json.loads(response.text)['token'])['u_id']

    # user_two ----> not a member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    
    # Login user_one to create a public channel
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_1 , "name": "channel1", "is_public": True})
    channel_id = json.loads(response.text)['channel_id']

    # Implement details function with invalid channel_id (InputError 400)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_1, "channel_id": 1212})
    assert (response.status_code == 400)

    # Implement details function -----> successful implement
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_1, "channel_id": channel_id})
    assert (response.status_code == 200)
    assert (json.loads(response.text)==  { 
        'all_members': [{
            'email': 'testperson@email.com',
            'handle_str': 'testperson',
            'name_first': 'Test',
            'name_last': 'Person',
            'u_id': uid_1
            }],
        'is_public': True,
        'name': 'channel1',
        'owner_members': [{
            'email': 'testperson@email.com',
            'handle_str': 'testperson',
            'name_first': 'Test',
            'name_last': 'Person',
            'u_id': uid_1
        }],
    })

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================  

    # Login user_two 
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    # User with invalid token to implement function (AccessError 403)
    # token_1 is invalid already (same token formation)
    resp = requests.get(f'{BASE_URL}/channel/details/v2', params={"token": token_1, "channel_id": channel_id})
    assert (resp.status_code == 403)

    # User with invalid token and channel_id to implement function (AccessError 403)
    # token_1 is invalid already (same token formation)
    resp = requests.get(f'{BASE_URL}/channel/details/v2', params={"token": token_1, "channel_id": 123123})
    assert (resp.status_code == 403)

    # Implement details function (not a member of channel) (AccessError 403)
    resp = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})
    assert (resp.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')