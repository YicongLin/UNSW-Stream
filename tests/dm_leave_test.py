import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# ==================================
# Test dm_leave
# ==================================

def test_dm_leave():
    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> dm creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})

    # user_two ----> dm member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})

    # user_three ----> not member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})

    # Login user_one to create dm
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token_1, "u_ids": [1, 2]})
    dm_id = json.loads(response.text)['dm_id']

    # User with invalid token to implement function (AccessError 403)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "asdfgh", "dm_id": dm_id})
    assert (resp.status_code == 403)

    # Implement dm_leave with invalid dm_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (resp.status_code == 400)

    # User with invalid token and invalid dm_id to implement function (AccessError 403)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "asdfgh", "dm_id": 123123})
    assert (resp.status_code == 403)

    # Check dm_details(user_one and user_two)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_1, "dm_id": dm_id})
    assert (json.loads(response.text)== {   })

    # user_one leave dm -----> successful implement (creator leave)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (resp.status_code == 200)

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================
    
    # Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_3 = json.loads(response.text)['token']

    # Implement dm_leave (not member) (AccessError 403)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_3, "dm_id": dm_id})
    assert (resp.status_code == 403)

    # logout user_three
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_3})

    # ===================================
    # Switch user
    # ===================================  

    # login user_two
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']
 
    # Check dm_details(user_two)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_2, "dm_id": dm_id})
    assert (json.loads(response.text) == {   })

    # user_one leave dm -----> successful implement ()
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_2, "dm_id": dm_id})
    assert (resp.status_code == 200)

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')