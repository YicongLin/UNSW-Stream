""" testing for channels list """
import pytest
import requests
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import AccessError
from src.dm import dm_create_v1, dm_list_v1
import json
BASE_URL = 'http://127.0.0.1:2000'
# checking for invalid token, if a user is logged out that token is invalid
def test_invalid_token_list():
    """ auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        channels_list_v2(token) """
    
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "yicong", "name_last": "lin"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    response = requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})
    assert (response.status_code) == 200
    response = requests.get(f'{BASE_URL}/channels/list/v2', params={"token": token})
    assert (response.status_code) == 403
# test for a user that didn't join or create any channel
def test_empty_list():
    """ auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    assert channels_list_v2(token) == {
        'channels': [

        ]
    } """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test@gmail.com", "password": "password454643", "name_first": "yicong1", "name_last": "lin1"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    resp = requests.get(f'{BASE_URL}/channels/list/v2', params={"token": token})
    assert json.loads(resp.text) == {
        'channels': [

        ]
    }
    
def test_list():
    """ auth_register_v2("testing@gmail.com", "passwordsdhhfd", 'james', 'wang')
    login_return = auth_login_v2("testing@gmail.com", "passwordsdhhfd")
    token = login_return['token']
    channel_id = channels_create_v2(token, 'channel1', False)['channel_id']
    assert channels_list_v2(token) == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'channel1'
            }
        ]
    } """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testing@gmail.com", "password": "passwordsdhhfd", "name_first": "james", "name_last": "wang"})
    register_return = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test@gmail.com", "password": "password454643", "name_first": "yicong1", "name_last": "lin1"})
    u_id = json.loads(register_return.text)['auth_user_id']

    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testing@gmail.com", "password": "passwordsdhhfd"})
    token = json.loads(response.text)['token']
    
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']
    
    requests.post(f'{BASE_URL}/channel/invite/v2', json = {"token": token, "channel_id": channel_id, "u_id": u_id})
    resp = requests.get(f'{BASE_URL}/channels/list/v2', params={"token": token})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'channel1'
            }
        ]
    }
