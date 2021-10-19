import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# ==================================
# Test dm_details
# ==================================

# (1) register users
# (2) login user_one to create dm
# (3) Implement dm_details with invalid dm_id (InputError 400)
# (4) Show details of dm -----> successful implement
# (5) logout user_one

# (6) login user_two
# (7) Show details of dm -----> successful implement (same as previous output)
# (8) logout user_two

# (9) login user_three
# (10) Implement dm_details(no permissions) (AccessError 403)

# ==================================
# Specific token, dm_id and u_id will be replaced by var for next version
# Pytest following tests require relevant routes
# ==================================

# def test_dm_details():
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
#     response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "token_one", "dm_id": 123})
#     assert (response.status_code == 400)

#     #(4)
#     response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "token_one", "dm_id": 123})
#     response_data = response.json()
#     assert (response.status_code == 200)
#     assert (response_data['name'] == ["ahandle1", "userotwo_handle"])
#     assert (response_data['dm_members'] == 
#                 {
#                     'u_id': 1,
#                     'email':'1@email.com', 
#                     'name_first': 'a', 
#                     'name_last':'1last', 
#                     'handle_str': 'ahandle1'
#                 },

#                  {
#                     'u_id': 2,
#                     'email':'2@email.com', 
#                     'name_first': 'b', 
#                     'name_last':'2last', 
#                     'handle_str': 'bhandle2'
#                 },)

#     #(5)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_one"})

#     #(6)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})

#     #(7)
#     response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "token_two", "dm_id": 123})
#     response_data = response.json()
#     assert (response.status_code == 200)
#     assert (response_data['name'] == ["ahandle1", "bhandle"])
#     assert (response_data['dm_members'] == 
#                 {
#                     'u_id': 1,
#                     'email':'1@email.com', 
#                     'name_first': 'a', 
#                     'name_last':'1last', 
#                     'handle_str': 'ahandle1'
#                 },

#                  {
#                     'u_id': 2,
#                     'email':'2@email.com', 
#                     'name_first': 'b', 
#                     'name_last':'2last', 
#                     'handle_str': 'bhandle2'
#                 },)

#     #(8)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_two"})

#     #(9)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})

#     #(10)
#     response = requests.get(f"{BASE_URL}/dm/details/v1", json={"token": "token_thr", "dm_id": 1})
#     assert (response.status_code == 403)
