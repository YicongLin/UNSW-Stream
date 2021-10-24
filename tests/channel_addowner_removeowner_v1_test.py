import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:2000'

# ==================================
# Test both addowner and removeowner (cooperate with details function)
# ==================================

def test_addowner_removeowner():
    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')
    
    # Register three users
    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    uid_1 = decode_JWT(json.loads(response.text)['token'])
    
    # user_two ----> channel owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    uid_2 = decode_JWT(json.loads(response.text)['token']) 

    # user_three ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})
    uid_3 = decode_JWT(json.loads(response.text)['token'])

    # Login in user_two to create channel (test owner permmisons)
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # Add owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": 123, "u_id": uid_1})
    assert (resp.status_code == 400)

    # Remove owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": 123, "u_id": uid_1})
    assert (resp.status_code == 400)

    # Add owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    # Remove owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    # Add user_one(not an member yet) as owner (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    # User_two invite user_one, user_three
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

    # Check channel details(owner_members: user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == 222)

    # Add user_one as owner-----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    # Check channel details(user_two, user_one)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == 111)

    # Add user_one as owner again(alreadt is an owner) (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    # Remove user_one owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    # Check channel details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == 222)

    # Remove user_one (not an owner yet) permissions (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 400)

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================   

    # login user_one 
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Add user_three as owner -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    # Check channel details(owner_members: user_two, user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == 2321)

    # Remove user_three owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    # Check channel details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", json={"token": token_1, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == 213)

    # Remove user_two(only owner) owner permissions ------> (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removewner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_2})
    assert (resp.status_code == 400)

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================  

    # Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_3 = json.loads(response.text)['token']

    # Add user_one as owner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_3, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    # Remove user_one owner permissions (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_3, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 403)

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')