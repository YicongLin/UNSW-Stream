import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.token_helpers import decode_JWT
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1
from src.other import clear_v1

BASE_URL = 'http://127.0.0.1:7000'

# Creating valid tokens and ids
@pytest.fixture
def valid():
    clear_v1()
    # tokens
    token_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['token']
    token_2 = auth_register_v2("asd@fgh.com", "password", "jkl", "asd")['token']
    token_3 = auth_register_v2("abc@def.com", "password", "ghi", "jkl")['token']

    # token_1: id_1 
    # global owner
    decoded_token = decode_JWT(token_1)
    id_1 = decoded_token['u_id']

    # token_2: id_2
    decoded_token = decode_JWT(token_2)
    id_2 = decoded_token['u_id']

    # token_3: id_3
    decoded_token = decode_JWT(token_3)
    id_3 = decoded_token['u_id']


    return token_1, token_2, token_3, id_1, id_2, id_3
 
# Testing for invalid u_id
def test_invalid_u_id():
    clear_v1()

    # register and login first user
    payload = {"email": "qwe@rty.com", "password": "password", "name_first": "uio", "name_last": "qwe"
    }
    requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "qwe@rty.com", "password": "password"})
    resp = r.json()

    # first user changes permission of an invalid user
    payload = {"token": resp['token'], "u_id": "invalid id", "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(valid):
    clear_v1()
    token_1, token_2, _, id_1, _, id_3 = valid
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token_1})
    payload = {
        "token": token_1,
        "u_id": id_3,
        "permission_id": 2
    }
    '''r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400
    # login first user
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "qwe@rty.com", "password" : "password"})
    resp1 = r.json()

    # register and login second user
    payload = {"email": "hi@bye.com", "password": "password", "name_first": "hi", "name_last": "bye"}
    requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "hi@bye.com", "password" : "password"})
    resp2 = r.json()

    # first user logs out
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp1['token']})

    # first user attempts to demote id_2
    payload = {"token": resp1['token'], "u_id": resp2['auth_user_id'], "permission_id": 1}
    '''
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where u_id is the only global owner 
# and they are being demoted
def test_global_owner_demoted(valid):
    requests.delete(f'{BASE_URL}/clear/v1')
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "qwe@rty.com", "password": "password"})
    resp = r.json()
    token_1, token_2, _, id_1, id_2, _ = valid
    payload = {
        "token": token_1,
        "u_id": id_1,
        "permission_id": 2
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid permission_id
def test_invalid_permission_id(valid):
    token_1, _, _, _, id_2, _ = valid
    payload1 = {
        "token": token_1,
        "u_id": id_2,
        "permission_id": 3
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload1)
    assert r.status_code == 400

# # Testing for a case where the authorised user is not a global owner
# def test_not_global(valid):
#     _, _, token_3, _, id_2, _, = valid
#     payload = {
#         "token": token_3,
#         "u_id": id_2,
#         "permission_id": 2
#     }
#     r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
#     assert r.status_code == 403

# Test valid case
def test_valid(valid):
    token_1, _, _, _, id_2, _ = valid
    payload = {
        "token": token_1,
        "u_id": id_2,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 200

# Assert that permission_id has been changed
def test_changed(valid):
    token_1, token_2, _, _, id_2, id_3 = valid

    # id_1 promotes id_2 to global owner
    payload1 = {
        "token": token_1,
        "u_id": id_2,
        "permission_id": 1
    }
    requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload1)

    # assert that id_2's permissions have been changed;
    # id_2 should now be able to promote id_3
    payload2 = {
        "token": token_2,
        "u_id": id_3,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload2)
    assert r.status_code == 200
