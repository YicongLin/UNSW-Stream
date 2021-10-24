import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.token_helpers import decode_JWT
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens and ids and a valid channel and dm
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

    return token_1, token_2, token_3, id_1, id_2, id_3, 


# Testing for invalid u_id
def test_invalid_u_id(valid):
    token_1, *_ = valid
    payload = {
        "token": token_1,
        "u_id": "invalid id",
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(valid):
    _, _, _, _, id_2, _ = valid
    payload = {
        "token": "invalid token",
        "u_id": id_2,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400

# Testing for a case where u_id is the only global owner 
# and they are being demoted
def test_global_owner_demoted(valid):
    token_1, _, _, id_1, *_ = valid
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

    # invalid integer
    payload1 = {
        "token": token_1,
        "u_id": id_2,
        "permission_id": 3
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload1)
    assert r.status_code == 400

    # string
    payload2 = {
        "token": token_1,
        "u_id": id_2,
        "permission_id": "invalid"
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload2)
    assert r.status_code == 400

# Testing for a case where the authorised user is not a global owner
def test_not_global(valid):
    _, token_2, _, _, _, id_3 = valid
    payload = {
        "token": token_2,
        "u_id": id_3,
        "permission_id": 1
    }
    r = requests.post(f'{BASE_URL}/admin/userpermission/change/v1', json = payload)
    assert r.status_code == 400

# Test valid case
def test_valid(valid)
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

