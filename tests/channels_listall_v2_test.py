import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'
 
# ==================================
# Test listall function
# ==================================

def test_listall():
    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> public channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})

    # user_two ----> private channel creator
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})

    # user_three ----> implement listall function
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})

    # Login user_one to create a public channel
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_1 , "name": "channel1", "is_public": True})

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})
    # ===================================
    # Switch user
    # ===================================  

    # Login user_two to create a privite channel
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================  

    # Login user_three
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_3 = json.loads(response.text)['token']

    # User with invalid token to implement function (AccessError 403)
    resp = requests.get(f'{BASE_URL}/channels/listall/v2', json={"token": 1231213})
    assert (resp.status_code == 403)

    # Implement listall function -----> successful implement
    response = requests.get(f'{BASE_URL}/channels/listall/v2', json={"token": token_3})
    assert (response.status_code == 200)
    assert (json.loads(response.text) == {})

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')