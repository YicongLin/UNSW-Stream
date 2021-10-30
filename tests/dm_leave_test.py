import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:3178'

# ==================================
# Test dm_leave
# ==================================

def test_dm_leave():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # Register three users
    # user_one ----> dm creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    uid_1 = decode_JWT(json.loads(response.text)['token'])['u_id']

    # user_two ----> dm member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    uid_2 = decode_JWT(json.loads(response.text)['token'])['u_id']

    # user_three ----> not member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})

    # user_four ----> dm member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonfour@email.com", "password": "passwordfour", "name_first": "Testfour", "name_last": "Personfour"})
    uid_4 = decode_JWT(json.loads(response.text)['token'])['u_id']  

    # Login user_one to create dm
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token_1, "u_ids": [uid_2, uid_4]})
    dm_id = json.loads(response.text)['dm_id']

    # Implement dm_leave with invalid dm_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": 123123})
    assert (resp.status_code == 400)

    # Check dm_details(user_one, user_two, user_four)
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_1, "dm_id": dm_id})
    assert (json.loads(response.text) == {
        'members': [
            {'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2},

            {'email': 'testpersonfour@email.com',
            'handle_str': 'testfourpersonfour',
            'name_first': 'Testfour',
            'name_last': 'Personfour',
            'u_id': uid_4},

            {'email': 'testperson@email.com',
            'handle_str': 'testperson',
            'name_first': 'Test',
            'name_last': 'Person',
            'u_id': uid_1}
            ],
        'name': ['testfourpersonfour', 'testperson', 'testtwopersontwo'],
    })

    # user_one leave dm -----> successful implement (creator leave)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (resp.status_code == 200)

    # User cannot access dm details after leave (AccessError 403)
    resp = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_1, "dm_id": dm_id})
    assert (resp.status_code == 403)

    # Logout user_one
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_1})

    # User with invalid token to implement function (AccessError 403)
    # token_1 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": dm_id})
    assert (resp.status_code == 403)

    # User with invalid token and invalid dm_id to implement function (AccessError 403)
    # token_1 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_1, "dm_id": 123123})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================
    
    # Login user_three
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr"})
    token_3 = json.loads(response.text)['token']

    # Implement dm_leave (not member) (AccessError 403)
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_3, "dm_id": dm_id})
    assert (resp.status_code == 403)

    # logout user_three
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_3})

    # ===================================
    # Switch user
    # ===================================  

    # login user_two
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    # Check dm_details(user_two, user_four)
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_2, "dm_id": dm_id})
    assert (json.loads(response.text) == {
        'members': [
            {'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2},

            {'email': 'testpersonfour@email.com',
            'handle_str': 'testfourpersonfour',
            'name_first': 'Testfour',
            'name_last': 'Personfour',
            'u_id': uid_4},

            ],
        'name': ['testfourpersonfour', 'testperson', 'testtwopersontwo'],
    })

    # user_two leave dm -----> successful implement
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_2, "dm_id": dm_id})
    assert (resp.status_code == 200)

    # User cannot access dm details after leave (AccessError 403)
    resp = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_2, "dm_id": dm_id})
    assert (resp.status_code == 403)

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================  

    # login user_four
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonfour@email.com", "password": "passwordfour"})
    token_4 = json.loads(response.text)['token']

    # Check dm_details(user_four)
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": token_4, "dm_id": dm_id})
    assert (json.loads(response.text) == {
        'members': [
            {'email': 'testpersonfour@email.com',
            'handle_str': 'testfourpersonfour',
            'name_first': 'Testfour',
            'name_last': 'Personfour',
            'u_id': uid_4},
            ],
        'name': ['testfourpersonfour', 'testperson', 'testtwopersontwo'],
    })

    # user_four leave dm(only member) -----> successful implement
    resp = requests.post(f'{BASE_URL}/dm/leave/v1', json={"token": token_4, "dm_id": dm_id})
    assert (resp.status_code == 200)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')