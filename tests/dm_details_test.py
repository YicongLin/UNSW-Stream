import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:1024'

# ==================================
# Test dm_details
# ==================================

def test_dm_details():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> dm creator
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})

    # user_two ----> dm member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    uid_2 = decode_JWT(json.loads(response.text)['token']) ['u_id']

    # user_three ----> not member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})

    # Login user_one to create dm
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token_1, "u_ids": [uid_2]})
    dm_id = json.loads(response.text)['dm_id']
    assert json.loads(response.text) == {"dm_id": dm_id}

    # Implement dm_details with invalid dm_id (InputError 400)
    resp = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_1, "dm_id": 123})
    assert (resp.status_code == 400)

    # User with invalid token to implement function (AccessError 403)
    resp = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": "asdfgh", "dm_id": dm_id})
    assert (resp.status_code == 403)

    # User with invalid token and invalid dm_id to implement function (AccessError 403)
    resp = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": "asdfgh", "dm_id": 123123})
    assert (resp.status_code == 403)

    # Show details of dm -----> successful implement
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_1, "dm_id": dm_id})
    assert (response.status_code == 200)
    # assert (json.loads(response.text) == {   })

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================

    # Login user_two
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_2 = json.loads(response.text)['token']

    # Show details of dm -----> successful implement (same as previous output)
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_2, "dm_id": dm_id})
    assert (response.status_code == 200)
    # assert (json.loads(response.text) == {   })

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================

    # Login user_three
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_3 = json.loads(response.text)['token']

    # Implement dm_details(no a member) (AccessError 403)
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_3, "dm_id": dm_id})
    assert (response.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')