import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:2000'

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

def test_addowner_removeowner():
    # requests.delete(f'{BASE_URL}/clear/v1')
    
    #(1) Register three users
    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
    response_data = response.json()
    token_1 = response_data['token']
    uid_1 = decode_JWT(token_1)

    # user_two ----> channel owner
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"})
    response_data = response.json()
    token_2 = response_data['token']
    uid_2 = decode_JWT(token_2) 

    # user_three ----> channel member
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})
    response_data = response.json()
    token_3 = response_data['token'] 
    uid_3 = decode_JWT(token_3)

    #(2) login in user_two to create channel (test owner permmisons)
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    response_data = response.json()
    token_2 = response_data['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    response_data = response.json()
    channel_id = response_data['channel_id']

    #(3) Add owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": 123, "u_id": uid_1})
    assert (resp.status_code == 400)

    #(4) Remove owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": 123, "u_id": uid_1})
    assert (resp.status_code == 400)

    #(5) Add owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    #(6) Remove owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    #(7) Add user_one(not an member yet) as owner (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    #(8) user_two invite user_one, user_three
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})

    # User with invalid token to addowner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": "asdfgh", "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    # User with invalid token to removeowner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": "asdfgh", "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    # User with invalid token, channel_id and u_id to addowner(RaiseError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": "asdfgh", "channel_id": 123, "u_id": 123})
    assert (resp.status_code == 403)

    # User with invalid token, channel_id and u_id to removeowner(RaiseError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": "asdfgh", "channel_id": 123, "u_id": 123})
    assert (resp.status_code == 403)

    #(9) Check channel details(owner_members: user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    response_data = response.json()  
    assert (response_data['owner_members'] == 222) # need to update===============================

    #(10) Add user_one as owner-----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    #(11) Check channel details(owner_members: user_two, user_one)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    response_data = response.json()
    assert (response_data['owner_members'] == 111)  # need to update===============================

    #(12) Add user_one as owner again(alreadt is an owner) (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    #(13) Remove user_one owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    #(14) check channel details(owner_members: user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    response_data = response.json()
    assert (response_data['owner_members'] == 222)

    #(15) Remove user_one (not an owner yet) permissions (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    #(16) Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_2})
    # ===================================
    # Change user
    # ===================================   
    #(17) login user_one 
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    response_data = response.json()
    token_1 = response_data['token']

    #(18) Add user_three as owner -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    #(19) check channel details(owner_members: user_two, user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": channel_id})
    response_data = response.json()
    assert (response_data['owner_members'] == 2321)

    #(20) Remove user_three owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    #(21) check channel details(owner_members: user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": channel_id})
    response_data = response.json()
    assert (response_data['owner_members'] == 213)

    #(22) Remove user_two(only owner) owner permissions ------> (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_2})
    assert (resp.status_code == 400)

    #(23) logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})
    # ===================================
    # Change user
    # ===================================  
    #(24) Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    token_3 = response_data['token']

    #(25) Add user_one as owner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_3, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    #(26) Remove user_one owner permissions (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_3, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    # requests.delete(f'{BASE_URL}/clear/v1')