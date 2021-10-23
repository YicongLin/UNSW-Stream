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
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
    response_data = response.json()
    token_1 = response_data['token']

    # user_two ----> private channel creator
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"})
    response_data = response.json()
    token_2 = response_data['token']

    # user_three ----> implement listall function
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})
    response_data = response.json()
    token_3 = response_data['token'] 

    # Login user_one to create a public channel
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    response_data = response.json()
    token_1 = response_data['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_1 , "name": "channel1", "is_public": True})
    response_data = response.json()

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_1})

    # ===================================
    # Switch user
    # ===================================  

    # Login user_two to create a privite channel
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    response_data = response.json()
    token_2 = response_data['token']

    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    response_data = response.json()

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================  

    # Login user_three
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    token_3 = response_data['token']

    # User with invalid token to implement function (AccessError 403)
    response = requests.get(f'{BASE_URL}/channels/listall/v2', json={"token": 1231213})
    response_data = response.json()
    assert (response.status_code == 403)

    # Implement listall function -----> successful implement
    response = requests.get(f'{BASE_URL}/channels/listall/v2', json={"token": token_3})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (response_data == {})

    # Clear
    # requests.delete(f'{BASE_URL}/clear/v1')