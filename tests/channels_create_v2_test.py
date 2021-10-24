import pytest
import requests
from requests.api import request
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import InputError, AccessError
import json
BASE_URL = 'http://127.0.0.1:3178'
# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    """ auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        channels_create_v2(token, 'name', True) """

    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})

    # try to create a channel using invalid token
    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})
    assert (response.status_code) == 403

def test_invalid_input():
    """ auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    with pytest.raises(InputError):
        channels_create_v2(token, '', False)
        channels_create_v2(token, 'abfbabbcabdkbrafbakbfkab', False)
        channels_create_v2(token, '', True)
        channels_create_v2(token, 'dfdsjhkjhsdshkjfkjsdfjhjksdf  ', True) """

    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test@gmail.com", "password": "password454643", "name_first": "yicong", "name_last": "lin"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "", "is_public": True})
    assert (response.status_code) == 400

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "abfbabbcabdkbrafbakbfkab", "is_public": True})
    assert (response.status_code) == 400
    
    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "", "is_public": False})
    assert (response.status_code) == 400

    response = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "dfdsjhkjhsdshkjfkjsdfjhjksdf  ", "is_public": True})
    assert (response.status_code) == 400

def test_channel_succesfully_created():
    auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']  
    channel_id = channels_create_v2(token, 'channel1', True)['channel_id']
    assert channels_list_v2(token) == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'channel1'
            }
        ]
    }
 

