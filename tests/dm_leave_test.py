import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# ==================================
# Test dm_leave
# ==================================

# (1) register users
# (2) login user_one to create dm
# (3) Implement dm_leave with invalid dm_id (InputError 400)
# (4) user_one leave dm -----> successful implement (creator leave)
# (5) logout user_one

# (6) login user_three
# (7) Implement dm_leave (not member) (AccessError 403)
# (8) logout user_three

# (9) login user_two
# (10) Implement dm_details for visual check leave implementation
# (11) user_one leave dm -----> successful implement ()


def test_dm_leave():
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

    # User with invalid token to implement function (AccessError 403)
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "asdfgh", "dm_id": dm_id})
    assert (response.status_code == 403)

    # Implement dm_leave with invalid dm_id (InputError 400)
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (response.status_code == 400)

    # User with invalid token and invalid dm_id to implement function (AccessError 403)
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "asdfgh", "dm_id": 123123})
    assert (response.status_code == 403)

    # Check dm_details(user_one and user_two)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_1, "dm_id": dm_id})
    response_data = response.json()
    assert (response_data == {   })

    # user_one leave dm -----> successful implement (creator leave)
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (response.status_code == 200)

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================
    
    # Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    token_3 = response_data['token']

    # Implement dm_leave (not member) (AccessError 403)
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_3, "dm_id": dm_id})
    assert (response.status_code == 403)

    # logout user_three
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_3})

    # ===================================
    # Switch user
    # ===================================  

    # login user_two
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    response_data = response.json()
    token_2 = response_data['token']
 
    # Check dm_details(user_two)
    response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": token_2, "dm_id": dm_id})
    response_data = response.json()
    assert (response_data == {   })

    # user_one leave dm -----> successful implement ()
    response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_2, "dm_id": dm_id})
    assert (response.status_code == 200)

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')