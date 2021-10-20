import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'
 
# ==================================
# Test listall function
# ==================================

# (1) register users
# (2) login user_one to create a public channel
# (3) logout user_one

# (4) login user_two to create a privite channel
# (5) logout user_two

# (6) login user_three
# (7) Implement listall function -----> successful implement


def test_listall():
    #(1)
    requests.delete(f'{BASE_URL}/clear/v1')
    # user_one ----> public channel creator
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "Firstname": "Test", "Lastname": "Person"})
    # user_two ----> private channel creator
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "Firstname": "Testtwo", "Lastname": "Persontwo"}) 
    # user_three ----> implement listall function
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "Firstname": "Testthr", "Lastname": "Personthr"})

    #(2)
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": "token_two", "name": "channel1", "is_public": True})

    #(3)
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_one"})

    #(4)
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": "token_two", "name": "channel2", "is_public": False})

    #(5)
    requests.post(f'{BASE_URL}/auth/logout/v2', json={"token": "token_two"})

    #(6)
    response = requests.get(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response = requests.get(f'{BASE_URL}/channels/listall/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    response_data = response.json()
    assert (response.status_code == 400)
    assert (response_data == {"channels": [ {'channel_id': 1, 'name': 'channel1'}, {'channel_id': 2, 'name': 'channel2'} ] })

