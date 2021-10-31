""" testing for  """
import pytest
import requests
import json

BASE_URL = 'http://127.0.0.1:3178'
# checking for invalid token, if a user is logged out that token is invalid
def test_invalid_token_remove():
    """ auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_remove_v1(token, dm_id) """

    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']
    
    store = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": []})
    dm_id = json.loads(store.text)['dm_id']
    
    response = requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})
    assert (response.status_code) == 200
    
    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": token, "dm_id": dm_id})
    assert (response.status_code) == 403

    

# check if the token passed in is the creator of the dm, if not raise access error
def test_not_creator():
    
    """ auth_register_v2("test35@gmail.com", "password454643", "darren", "gao")
    auth_register_v2("test21@gmail.com", "password454643", "anthony", "huang")
    gao_login_return = auth_login_v2("test35@gmail.com", "password454643")
    huang_login_return = auth_login_v2("test21@gmail.com", "password454643")
    gao_token = gao_login_return['token']
    huang_token = huang_login_return['token']
    huang_id = huang_login_return['auth_user_id']
    dm_id = dm_create_v1(gao_token, [huang_id])['dm_id']

    with pytest.raises(AccessError):
        dm_remove_v1(huang_token, dm_id) """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test35@gmail.com", "password": "password454643", "name_first": "darren", "name_last": "gao"})
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test21@gmail.com", "password": "password454643", "name_first": "anthony", "name_last": "huang"})

    darren = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test35@gmail.com", "password": "password454643"})
    anthony = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test21@gmail.com", "password": "password454643"})
    
    darren_token = json.loads(darren.text)['token']
    anthony_token = json.loads(anthony.text)['token']

    anthony_id = json.loads(anthony.text)['auth_user_id']

    create_return = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": darren_token, "u_ids": [anthony_id]})
    dm_id = json.loads(create_return.text)['dm_id']

    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": anthony_token, "dm_id": dm_id})
    assert (response.status_code) == 403
# if the dm id is not found in the dm datastore, raise input error
def test_invalid_dm():

    """ auth_register_v2("test53@gmail.com", "password454643", "amy", "chen")
    login_return = auth_login_v2("test53@gmail.com", "password454643")
    token = login_return['token']
    dm_create_v1(token, [])
    with pytest.raises(InputError):
        dm_remove_v1(token, -1)
        dm_remove_v1(token, 0)
        dm_remove_v1(token, -100) """
    requests.delete(f'{BASE_URL}/clear/v1')
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test53@gmail.com", "password": "password454643", "name_first": "amy", "name_last": "chen"})
    amy = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test53@gmail.com", "password": "password454643"})
    token = json.loads(amy.text)['token']
    requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": []})

    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": token, "dm_id": -1})
    assert (response.status_code) == 400

    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": token, "dm_id": 0})
    assert (response.status_code) == 400

    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": token, "dm_id": -100})
    assert (response.status_code) == 400
# create a dm and remove, and try to list it out to see if it's empty
def test_remove_dm():
    
    """ anna_id = auth_register_v2("test99@gmail.com", "password454643", "anna", "li")['auth_user_id']
    auth_register_v2("test89@gmail.com", "password454643", "anne", "li")
    login_return = auth_login_v2("test89@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [anna_id])['dm_id']
    dm_remove_v1(token, dm_id)
    assert dm_list_v1(token) == {
        'dms': [

        ]
    } """

    requests.delete(f'{BASE_URL}/clear/v1')
    anna = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test99@gmail.com", "password": "password454643", "name_first": "anna", "name_last": "li"})
    anna_id = json.loads(anna.text)['auth_user_id']
    
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "test89@gmail.com", "password": "password454643", "name_first": "anne", "name_last": "li"})

    anne = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "test89@gmail.com", "password": "password454643"})
    token = json.loads(anne.text)['token']

    create_return = requests.post(f'{BASE_URL}/dm/create/v1', json={"token": token, "u_ids": [anna_id]})
    dm_id = json.loads(create_return.text)['dm_id']

    requests.delete(f'{BASE_URL}/dm/remove/v1', json={"token": token, "dm_id": dm_id})

    resp = requests.get(f'{BASE_URL}/dm/list/v1', params={"token": token})
    assert json.loads(resp.text) == {
        'dms': [

        ]
    }
