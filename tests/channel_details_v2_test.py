import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:8080'
 
# ==================================
# Test channel_details function
# ==================================

# (1) register two users
# (2) login user_one to create a public channel
# (3) Implement details function with invalid channel_id (InputError 400)
# (4) Implement details function -----> successful implement
# (5) logout user_one

# (6) login user_two 
# (7) Implement details function (not a member of channel) (AccessError 403)

    
def test_channel_details():
    # requests.delete(f'{BASE_URL}/clear/v1')

    #(1) Register two users

    # user_one ----> channel creator (only member)
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
    response_data = response.json()
    token_1 = response_data['token']

    # user_two ----> not a member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"})
    response_data = response.json()
    token_2 = response_data['token']

    #(2) Login user_one to create a public channel
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    response_data = response.json()
    token_1 = response_data['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_1 , "name": "channel1", "is_public": False})
    response_data = response.json()
    channel_id = response_data['channel_id']

    #(3) Implement details function with invalid channel_id (InputError 400)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": 123})
    assert (response.status_code == 400)

    #(4) Implement details function -----> successful implement
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": channel_id})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (response_data == 123123)

    # User with invalid token to implement function (AccessError 403)
    resp = requests.get(f'{BASE_URL}/channel/details/v2', json={"token": "asdfgh", "channel_id": channel_id})
    assert (resp.status_code == 403)

    # User with invalid token and channel_id to implement function (AccessError 403)
    resp = requests.get(f'{BASE_URL}/channel/details/v2', json={"token": "asdfgh", "channel_id": "asdfgh"})
    assert (resp.status_code == 403)

    #(5) Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})
    # ===================================
    # Change user
    # ===================================  
    #(6) Login user_two 
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    response_data = response.json()
    token_2 = response_data['token']

    #(7) Implement details function (not a member of channel) (AccessError 403)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    assert (response.status_code == 403)

    # requests.delete(f'{BASE_URL}/clear/v1')