""" testing for dm list """
import pytest
import requests
import json
from src.channels import channels_create_v2
from src.auth import auth_logout_v1, auth_register_v2, auth_login_v2
from src.error import AccessError
from src.dm import dm_create_v1, dm_list_v1
BASE_URL = 'http://127.0.0.1:48005'
# checking for invalid token, if a user is logged out that token is invalid
def test_invalid_token_dm_list():
    """ auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_list_v1(token) """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    response = requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})
    assert (response.status_code) == 200
    response = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert (response.status_code) == 403

# only the creator is in the dm
def test_list_only_creator():
    """ auth_register_v2("test@gmail.com", "password454643", "john", "smith")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    
    dm_id = dm_create_v1(token, [])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['johnsmith']
            }
        ]
    } """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test@gmail.com", "password": "password454643", "name_first": "john", "name_last": "smith"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']

    create_return = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": []})
    dm_id = json.loads(create_return.text)['dm_id']
    resp = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert json.loads(resp.text) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': 'johnsmith'
            }
        ]
    }
# a dm of 5 people
def test_list():
    """ auth_register_v2("test1@gmail.com", "password454643", "yicong", "lin")
    zami_id = auth_register_v2("test3@gmail.com", "password454643", "zami", "lee")['auth_user_id']
    lilian_id = auth_register_v2("test4@gmail.com", "password454643", "lilian", "pok")['auth_user_id']
    kang_id = auth_register_v2("test2@gmail.com", "password454643", "kang", "liu")['auth_user_id']
    prasannaa_id = auth_register_v2("test5@gmail.com", "password454643", "prasannaa", "pandey")['auth_user_id']


    login_return = auth_login_v2("test1@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [kang_id, zami_id, lilian_id, prasannaa_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['kangliu', 'lilianpok', 'prasannaapandey', 'yiconglin', 'zamilee']
            }
        ]
    } """

    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test1@gmail.com", "password": "password454643", "name_first": "yicong", "name_last": "lin"})
    zami = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test3@gmail.com", "password": "password454643", "name_first": "zami", "name_last": "lee"})
    lilian = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test4@gmail.com", "password": "password454643", "name_first": "lilian", "name_last": "pok"})
    kang = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test2@gmail.com", "password": "password454643", "name_first": "kang", "name_last": "liu"})
    prasannaa = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test5@gmail.com", "password": "password454643", "name_first": "prasannaa", "name_last": "pandey"})

    zami_id = json.loads(zami.text)['auth_user_id']
    lilian_id = json.loads(lilian.text)['auth_user_id']
    kang_id = json.loads(kang.text)['auth_user_id']
    prasannaa_id = json.loads(prasannaa.text)['auth_user_id']

    login = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test1@gmail.com", "password": "password454643"})
    token = json.loads(login.text)['token']
    store = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [zami_id, lilian_id, kang_id, prasannaa_id]})
    dm_id = json.loads(store.text)['dm_id']

    resp = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert json.loads(resp.text) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': 'kangliu, lilianpok, prasannaapandey, yiconglin, zamilee'
            }
        ]
    }

def test_list1():
    """ auth_register_v2("testa@gmail.com", "password454643", "jike", "zhang")
    long_id = auth_register_v2("testb@gmail.com", "password454643", "long", "ma")['auth_user_id']
    xin_id = auth_register_v2("testc@gmail.com", "password454643", "xin", "xu")['auth_user_id']
    login_return = auth_login_v2("testa@gmail.com", "password454643")
    token = login_return['token']

    dm_id = dm_create_v1(token, [long_id, xin_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['jikezhang', 'longma', 'xinxu']
            }
        ]
    } """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testa@gmail.com", "password": "password454643", "name_first": "jike", "name_last": "zhang"})
    long = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testb@gmail.com", "password": "password454643", "name_first": "long", "name_last": "ma"})
    xin = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testc@gmail.com", "password": "password454643", "name_first": "xin", "name_last": "xu"})

    long_id = json.loads(long.text)['auth_user_id']
    xin_id = json.loads(xin.text)['auth_user_id']

    login = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testa@gmail.com", "password": "password454643"})
    token = json.loads(login.text)['token']

    store = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [long_id, xin_id]})
    dm_id = json.loads(store.text)['dm_id']

    resp = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert json.loads(resp.text) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': 'jikezhang, longma, xinxu'
            }
        ]
    }
