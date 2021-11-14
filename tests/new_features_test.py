import pytest
import requests
import json
from src.token_helpers import decode_JWT
from src.config import url

BASE_URL = url

def test_rename_channel():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})

    # user_two ----> channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})

    # user_three ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})
    decoded_token_3 = decode_JWT(json.loads(response.text)['token'])
    uid_3 = decoded_token_3['u_id']

    # Login in user_two to create channel (test owner permmisons)
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # User_two invite user_one, user_three
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})

    # Check channel's name in channels
    response = requests.get(f'{BASE_URL}/channels/listall/v2', params={"token": token_2})
    assert (json.loads(response.text) == {'channels': [{'channel_id': channel_id, 'name': 'channel1'}]})

    # Check channel's name in channels_details
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})    
    assert (json.loads(response.text)['name'] == 'channel1')

    # Implement channel_rename with an invalid channel_id
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_2 , "channel_id": 123123, "new_name": "New channel name"})
    assert (resp.status_code == 400)

    # Implement channel_rename with a too long new name
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_2 , "channel_id": 123123, "new_name": "thasdoanckzxncjabsucbauscbauadcnaoc"})
    assert (resp.status_code == 400)

    # Implement channel_rename -----> successful implement
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_2 , "channel_id": channel_id, "new_name": "New channel name"})
    assert (resp.status_code == 200)

    # Check channel's name in channels
    response = requests.get(f'{BASE_URL}/channels/listall/v2', params={"token": token_2})
    assert (json.loads(response.text) == {'channels': [{'channel_id': channel_id, 'name': 'New channel name'}]})

    # Check channel's name in channels_details
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})    
    assert (json.loads(response.text)['name'] == 'New channel name')

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # User with invalid token to rename channel (AccessError 403)
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_2 , "channel_id": channel_id, "new_name": "New channel name"})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================  

    # Login user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_3 = json.loads(response.text)['token']

    # User_three try to rename channel (not a channel owner yet) (AccessError 403)
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_3 , "channel_id": channel_id, "new_name": "New channel name"})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================  

    # Login user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_1 = json.loads(response.text)['token']

    # User_one(global owner) try to rename channel (not a channel owner yet) (AccessError 403)
    resp = requests.put(f'{BASE_URL}/channel/rename/v1', json={"token": token_1 , "channel_id": channel_id, "new_name": "New channel name"})
    assert (resp.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')


