""" testing for dm_create """
import pytest
from src.channels import channels_create_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.dm import dm_create_v1, dm_list_v1

BASE_URL = 'http://127.0.0.1:2000'
import json
import requests
# checking for invalid token, if a user is logged out that token is invalid
def test_invalid_token_dm_create():
    """ auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_create_v1(token, []) """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    # requests.post(f'{BASE_URL}/auth/register/v2', json={"token": token})

    response = requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})
    assert (response.status_code) == 200
    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": []})
    assert (response.status_code) == 403
# create a dm of 2 people    
def test_dm_create():
    """ auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    register_return = auth_register_v2("test1@gmail.com", "password454643", "kevin", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    
    token = login_return['token']
    u_id = register_return['auth_user_id']
    dm_id = dm_create_v1(token, [u_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['kevinlin', 'yiconglin']
            }
        ]
    } """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test@gmail.com", "password": "password454643", "name_first": "yicong", "name_last": "lin"})
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "lin"})
    u_id = json.loads(response.text)['auth_user_id']
    login = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test@gmail.com", "password": "password454643"})
    token = json.loads(login.text)['token']
    store = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [u_id]})
    dm_id = json.loads(store.text)['dm_id']
    value = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert json.loads(value.text) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': 'kevinlin, yiconglin'
            }
        ]
    }


def test_invalid_id():
    """ auth_register_v2("test90@gmail.com", "password454643", "long", "chen")
    dan_id = auth_register_v2("test40@gmail.com", "password454643", "dan", "lin")['auth_user_id']
    login_return = auth_login_v2("test90@gmail.com", "password454643")
    token = login_return['token']
    with pytest.raises(InputError):
        dm_create_v1(token, [-9])
        dm_create_v1(token, [-9, 10, -11])
        dm_create_v1(token, [dan_id, -1]) """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test90@gmail.com", "password": "password454643", "name_first": "long", "name_last": "chen"})
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test40@gmail.com", "password": "password454643", "name_first": "dan", "name_last": "lin"})
    u_id = json.loads(response.text)['auth_user_id']
    login = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test40@gmail.com", "password": "password454643"})
    token = json.loads(login.text)['token']

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [-9]})
    assert (response.status_code) == 400

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [-9, 10, 11]})
    assert (response.status_code) == 400

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [u_id, -1]})
