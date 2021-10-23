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


# ==================================
# Specific token, dm_id will be replaced by var for next version
# Pytest following tests require relevant routes
# ==================================

# def test_dm_leave():
#     #(1)
#     requests.delete(f'{BASE_URL}/clear/v1')
#     # user_one ----> dm creator
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
#     # user_two ----> dm member
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"}) 
#     # user_three ----> not member
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})

#     #(2)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
#     requests.post(f'{BASE_URL}/dm/create/v1', json={"token": "token", "u_ids": [1, 2]})

#     #(3)
#     response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "token", "dm_id": 123})
#     assert (response.status_code == 400)

#     #(4)
#     response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "token", "dm_id": 1})
#     assert (response.status_code == 200)

#     #(5)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_one"})

#     #(6)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})

#     #(7)
#     response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "tokenthree", "dm_id": 1})
#     assert (response.status_code == 403)

#     #(8)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_three"})

#     #(9)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})

#     #(10)
#     response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "token_two", "dm_id": 123})
#     response_data = response.json()
#     assert (response.status_code == 200)
#     assert (response_data['name'] == ["bhandle"])
#     assert (response_data['dm_members'] == 
#                  {
#                     'u_id': 2,
#                     'email':'2@email.com', 
#                     'name_first': 'b', 
#                     'name_last':'2last', 
#                     'handle_str': 'bhandle2'
#                 },)

#     #(11)
#     response = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": "token_two", "dm_id": 1})
#     assert (response.status_code == 200)
