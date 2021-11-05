import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT

BASE_URL = 'http://127.0.0.1:3178'

# ==================================
# Test both addowner and removeowner 
# ==================================

def test_addowner_removeowner():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # Register three users
    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    decoded_token_1 = decode_JWT(json.loads(response.text)['token'])
    uid_1 = decoded_token_1['u_id']
    
    # user_two ----> channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    decoded_token_2 = decode_JWT(json.loads(response.text)['token']) 
    uid_2 = decoded_token_2['u_id']

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
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})

    # Check channel owner details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})    
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
    ])

    # Add user_one as owner-----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    # Check channel owner details(user_two, user_one)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
        {
            'email': 'testperson@email.com',
            'handle_str': 'testperson',
            'name_first': 'Test',
            'name_last': 'Person',
            'u_id': uid_1
        },
    ])

    # Remove user_one owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    assert (resp.status_code == 200)

    # Check channel owner details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})    
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
    ])

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # ===================================
    # Switch user
    # ===================================   

    # login user_one 
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Add user_three as owner -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    # Check channel owner details(user_two and user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_1, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
        {
            'email': 'testpersonthr@email.com',
            'handle_str': 'testthrpersonthr',
            'name_first': 'Testthr',
            'name_last': 'Personthr',
            'u_id': uid_3
        },
    ])

    # Remove user_three owner permissions -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_2})
    assert (resp.status_code == 200)

    # Check channel owner details(user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_1, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersonthr@email.com',
            'handle_str': 'testthrpersonthr',
            'name_first': 'Testthr',
            'name_last': 'Personthr',
            'u_id': uid_3
        },
    ])

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

# ========================================================================
# ========================================================================
# ========================================================================
# Test channel_addowner errors
# ========================================================================
# ========================================================================
# ========================================================================

def test_addowner_errors():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # user_two ----> channel creator & global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    decoded_token_2 = decode_JWT(json.loads(response.text)['token']) 
    uid_2 = decoded_token_2['u_id']

    # user_three ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})
    decoded_token_3 = decode_JWT(json.loads(response.text)['token'])
    uid_3 = decoded_token_3['u_id']

    # user_four ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonfour@email.com", "password": "passwordfour", "name_first": "Testfour", "name_last": "Personfour"})
    decoded_token_4 = decode_JWT(json.loads(response.text)['token'])
    uid_4 = decoded_token_4['u_id']

    # user_one 
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    decoded_token_1 = decode_JWT(json.loads(response.text)['token'])
    uid_1 = decoded_token_1['u_id']

    # Login in user_two to create channel (test owner permmisons)
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # Add owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    # Add user_three(not a member yet) as owner (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 400)

    # User_two invite user_one, user_three, user_four
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_4})

    # Add owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": 123, "u_id": uid_3})
    assert (resp.status_code == 400)    

    # Check channel owner details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
    ])

    # Add user_three as owner-----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)   

    # Check channel owner details(user_two and user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
        {
            'email': 'testpersonthr@email.com',
            'handle_str': 'testthrpersonthr',
            'name_first': 'Testthr',
            'name_last': 'Personthr',
            'u_id': uid_3
        },
    ])

    # Add user_one as owner again(already is an owner) (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 400)

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # User with invalid token to addowner (AccessError 403)
    # token_2 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 403)

    # User with invalid token with invalid channel_id to addowner(AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": 123123, "u_id": uid_3})
    assert (resp.status_code == 403)

    # User with invalid token with invalid u_id to addowner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123123})
    assert (resp.status_code == 403)

    # User with invalid token, channel_id and u_id to addowner(AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": 123123, "u_id": 123123})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================  

    # Login user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Add user_one as owner(no permissions) (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_4})
    assert (resp.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

# ========================================================================
# ========================================================================
# ========================================================================
# Test channel_removeowner errors
# ========================================================================
# ========================================================================
# ========================================================================

def test_removerowner_errors():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # user_one ----> global owner
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    decoded_token_1 = decode_JWT(json.loads(response.text)['token'])
    uid_1 = decoded_token_1['u_id']
    
    # user_two ----> channel creator
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo", "name_first": "Testtwo", "name_last": "Persontwo"})
    decoded_token_2 = decode_JWT(json.loads(response.text)['token']) 
    uid_2 = decoded_token_2['u_id']

    # user_three ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonthr@email.com", "password": "passwordthr", "name_first": "Testthr", "name_last": "Personthr"})
    decoded_token_3 = decode_JWT(json.loads(response.text)['token'])
    uid_3 = decoded_token_3['u_id']

    # user_four ----> channel member
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testpersonfour@email.com", "password": "passwordfour", "name_first": "Testfour", "name_last": "Personfour"})
    decoded_token_4 = decode_JWT(json.loads(response.text)['token'])
    uid_4 = decoded_token_4['u_id']

    # Login in user_two to create channel (test owner permmisons)
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersontwo@email.com", "password": "passwordtwo"})
    token_2 = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_2 , "name": "channel1", "is_public": False})
    channel_id = json.loads(response.text)['channel_id']

    # Remove owner with invalid u_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123})
    assert (resp.status_code == 400)

    # User_two invite user_one, user_three, user_four
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_1})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    requests.post(f'{BASE_URL}/channel/invite/v2', json={"token": token_2, "channel_id": channel_id, "u_id": uid_4})  

    # Remove user_three(not an owner yet) owner permission (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 400)

    # Remove user_two self's owner permission (only owner) (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_2})
    assert (resp.status_code == 400)

    # Add user_three as owner-----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/addowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)   

    # Check channel owner details(user_two and user_three)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_2, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
        {
            'email': 'testpersonthr@email.com',
            'handle_str': 'testthrpersonthr',
            'name_first': 'Testthr',
            'name_last': 'Personthr',
            'u_id': uid_3
        },
    ])

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_2})

    # User with invalid token to removeowner (AccessError 403)
    # token_2 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 403)

    # User with invalid token with invalid channel_id to removeowner(AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": 123123, "u_id": uid_3})
    assert (resp.status_code == 403)

    # User with invalid token with invalid u_id to removeowner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": channel_id, "u_id": 123123})
    assert (resp.status_code == 403)

    # User with invalid token, channel_id and u_id to removeowner (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_2, "channel_id": 123123, "u_id": 123123})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================  

    # Login user_four
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testpersonfour@email.com", "password": "passwordfour"})
    token_4 = json.loads(response.text)['token']

    # Remove user_three owner permission (AccessError 403)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_4, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 403)

    # ===================================
    # Switch user
    # ===================================  

    # Login user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Remove user_three owner permission -----> successful implement
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_3})
    assert (resp.status_code == 200)

    # Check channel owner details(user_two)
    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": token_1, "channel_id": channel_id})
    assert (json.loads(response.text)['owner_members'] == [{
            'email': 'testpersontwo@email.com',
            'handle_str': 'testtwopersontwo',
            'name_first': 'Testtwo',
            'name_last': 'Persontwo',
            'u_id': uid_2
        },
      ])

    # Remove owner with invalid channel_id (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_1, "channel_id": 123, "u_id": uid_3})
    assert (resp.status_code == 400) 

    # Remove user_two self's owner permission (only owner) (InputError 400)
    resp = requests.post(f'{BASE_URL}/channel/removeowner/v1', json={"token": token_1, "channel_id": channel_id, "u_id": uid_2})
    assert (resp.status_code == 400)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
