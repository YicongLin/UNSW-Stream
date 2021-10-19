import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# ==================================
# Test both addowner and removeowner (cooperate with details function)
# ==================================

# (1) register users
# (2) login in user_two to create channel (test owner permmisons)
# (3) Add owner with invalid channel_id (InputError 400)
# (4) Remove owner with invalid channel_id (InputError 400)
# (5) Add owner with invalid u_id (InputError 400)
# (6) Remove owner with invalid u_id (InputError 400)
# (7) Add user_one(not an member yet) as owner (InputError 400)
# (8) user_two invite user_one, user_three
# (9) check channel details(owner_members: user_two)
# (10) Add user_one as owner-----> successful implement
# (11) check channel details(owner_members: user_two, user_one)
# (12) Add user_one as owner again(alreadt is an owner) (InputError 400)
# (13) Remove user_one owner permissions -----> successful implement
# (14) check channel details(owner_members: user_two)
# (15) Remove user_one (not an owner yet) permissions (InputError 400)
# (16) logout user_two

# (17) login user_one 
# (18) Add user_three as owner -----> successful implement
# (19) check channel details(owner_members: user_two, user_three)
# (20) Remove user_three owner permissions -----> successful implement
# (21) check channel details(owner_members: user_two)
# (22) Remove user_two(only owner) owner permissions ------> (InputError 400)
# (23) logout user_one

# (24) login user_three
# (25) Add user_one as owner (AccessError 403)
# (26) Remove user_one owner permissions (AccessError 403)


# ==================================
# Specific token, channel_id and u_id will be replaced by var for next version
# Pytest following tests require relevant routes
# ==================================

# def test_removeowner():
#     #(1)
#     requests.delete(f'{BASE_URL}/clear/v1')
#     # user_one ----> global owner
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
#     # user_two ----> channel owner
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"}) 
#     # user_three ----> channel member
#     requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})

#     #(2)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
#     requests.post(f'{BASE_URL}/channels/create/v2', json={"token": "token_two", "name": "channel1", "is_public": False})

#     #(3)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_two", "channel_id": 123, "u_id": 1})
#     assert (resp.status_code == 400)

#     #(4)
#     resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": "token_two", "channel_id": 123, "u_id": 1})
#     assert (resp.status_code == 400)

#     #(5)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 123})
#     assert (resp.status_code == 400)

#     #(6)
#     resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 123})
#     assert (resp.status_code == 400)

#     #(7)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 400)

#     #(8)
#     requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": "token_two", "channel_id": 1, "u_id": 3})

#     #(9)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_two", "channel_id": 1})
#     response_data = response.json()
#     assert (len(response_data['owner_members']) == 1)
#     # assert (response_data['owner_members'][0]['u_id']) == 2)
#     assert (response_data['owner_members'][0]['u_id'] == 2)

#     #(10)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 200)

#     #(11)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_two", "channel_id": 1})
#     response_data = response.json()
#     assert (len(response_data['owner_members']) == 2)
#     assert (response_data['owner_members'][0]['u_id'] == 2 and response_data['owner_members'][1]['u_id'] == 1)

#     #(12)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 400)

#     #(13)
#     resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 200)

#     #(14)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_two", "channel_id": 1})
#     response_data = response.json()
#     assert (len(response_data['owner_members']) == 1)
#     assert (response_data['owner_members'][0]['u_id'] == 2)

#     #(15)
#     resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": "token_two", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 400)

#     #(16)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_two"})

#     #(17)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})

#     #(18)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_one", "channel_id": 1, "u_id": 3})
#     assert (resp.status_code == 200)

#     #(19)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_one", "channel_id": 1})
#     response_data = response.json()
#     assert (len(response_data['owner_members']) == 2)
#     assert (response_data['owner_members'][0]['u_id'] == 2 and response_data['owner_members'][1]['u_id'] == 3)

#     #(20)
#     resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": "token_one", "channel_id": 1, "u_id": 3})
#     assert (resp.status_code == 200)

#     #(21)
#     response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": "token_one", "channel_id": 1})
#     response_data = response.json()
#     assert (len(response_data['owner_members']) == 1)
#     assert (response_data['owner_members'][0]['u_id'] == 2)

#     #(22)
#     resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": "token_one", "channel_id": 1, "u_id": 2})
#     assert (resp.status_code == 400)

#     #(23)
#     requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_one"})

#     #(24)
#     requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})

#     #(25)
#     resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "token_thr", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 403)

#     #(26)
#     resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": "token_thr", "channel_id": 1, "u_id": 1})
#     assert (resp.status_code == 403)