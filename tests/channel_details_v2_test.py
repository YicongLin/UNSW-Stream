import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'
 
# ==================================
# Test channel_details function
# ==================================

# (1) register users
# (2) login user_one to create a public channel
# (3) Implement details function with invalid channel_id (InputError 400)
# (4) Implement details function -----> successful implement
# (5) logout user_one

# (6) login user_two 
# (7) Implement details function (not a member of channel) (AccessError 403)

    
# def test_chnnael_details():
#     #(1)
#     requests.delete(f'{BASE_URL}/clear/v1')
#     # user_one ----> channel creator (only member)
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
#     # user_two ----> not a member
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"}) 

#     #(2)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
#     requests.post(f'{BASE_URL}/channels/create/v2', json={"token": "token_two", "name": "channel1", "is_public": True})

#     #(3)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_one", "channel_id": 123})
#     assert (response.status_code == 400)

#     #(4)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_one", "channel_id": 1})
#     response_data = response.json()
#     assert (response.status_code == 200)
#     #assert (response_data = ..........)

#     #(5)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_two"})

#     #(6)
#     response = requests.get(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_two", "channel_id": 1})
#     assert (response.status_code == 403)