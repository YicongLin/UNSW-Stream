import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# ==================================
# Test dm_details
# ==================================

def test_dm_details():
    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> dm creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
    response_data = response.json()
    token_1 = response_data['token']

    # user_two ----> dm member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"})
    response_data = response.json()
    token_2 = response_data['token']

    # user_three ----> not member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})
    response_data = response.json()
    token_3 = response_data['token'] 

    # Login user_one to create dm
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    response_data = response.json()
    token_1 = response_data['token']

    requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token_1, "u_ids": [1, 2]})
    response_data = response.json()
    dm_id = response_data['dm_id']

    # Implement dm_details with invalid dm_id (InputError 400)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_1, "dm_id": 123})
    assert (response.status_code == 400)

    # User with invalid token to implement function (AccessError 403)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "asdfgh", "dm_id": dm_id})
    assert (response.status_code == 403)

    # User with invalid token and invalid dm_id to implement function (AccessError 403)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "asdfgh", "dm_id": 123123})
    assert (response.status_code == 403)


    # Show details of dm -----> successful implement
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_1, "dm_id": dm_id})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (response_data == {   })

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================

    # Login user_two
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    token_3 = response_data['token']

    # Show details of dm -----> successful implement (same as previous output)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_2, "dm_id": dm_id})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (response_data == {   })

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================

    # Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    token_3 = response_data['token']


    # Implement dm_details(no a member) (AccessError 403)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_3, "dm_id": dm_id})
    assert (response.status_code == 403)

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')