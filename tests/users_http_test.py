from flask.globals import request
import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.auth import auth_register_v2, auth_logout_v1, auth_login_v2

BASE_URL = 'http://127.0.0.1:3005'

#VALID IDS
@pytest.fixture
def valid_id():
    clear_v1()
    id_1 = auth_register_v2("testing@email.com", "password1", "first1", "last1")['auth_user_id']
    id_2 = auth_register_v2("anotherone@email.com", "password2", "hellllo", "world")['auth_user_id']
    token_1 = auth_login_v2("testing@email.com", "password1")['token']

    return id_1, id_2, token_1

# USERS ALL 
def test_users_all(valid_id):
    id_1, id_2, token_1 = valid_id

    # valid user 1
    payload = {
        "email" : "Ijks98ruwio@email.com",
        "password" : "password",
        "name_first" : "firstname",
        "name_last" : "lastname"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)   
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "Ijks98ruwio@email.com", "password" : "password"})
    assert (r.status_code == 200)  

    # valid token 
    resp = r.json()
    valid_token = resp['token']

    r = requests.get(f'{BASE_URL}/users/all/v1', params = {"token" : valid_token})
    assert (r.status_code == 200)

# USER PROFILE 
def test_user_profile():
    clear_v1() 
    # valid user 1
    payload = {
        "email" : "hjqbwsx@email.com",
        "password" : "password",
        "name_first" : "ehwjjskoo",
        "name_last" : "aishdufibjn"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 

    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "hjqbwsx@email.com", "password" : "password"})
    assert (r.status_code == 200) 

    payload = {
        "email" : "testio3@email.com",
        "password" : "password",
        "name_first" : "ehwjjskoo",
        "name_last" : "aishdufibjn"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    resp = r.json()

    # # valid token + valid id 
    # payload = {
    #     "token" : resp['token'],
    #     "u_id" : resp['auth_user_id']
    # } 

    r = requests.get(f'{BASE_URL}/user/profile/v1', params = payload)
    assert (r.status_code == 200) 
    
    # invalid uid
    payload = {
        "token" : resp['token'],
        "u_id" : 1263789
    }
    
    r = requests.get(f'{BASE_URL}/user/profile/v1', params = payload)
    assert (r.status_code == 400) 

    # logout
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    # invalid token
    payload = {
        "token" : resp['token'],
        "u_id" : resp['auth_user_id']
    }
    
    r = requests.get(f'{BASE_URL}/user/profile/v1', params = payload)
    
    assert (r.status_code == 403) 

    # test valid token, but not matching id 


# USER PROFILE SETNAME 
def test_user_profile_setname():
    clear_v1()

    # valid user 1
    payload = {
        "email" : "qwertyuiop@email.com",
        "password" : "password",
        "name_first" : "sjdnksand",
        "name_last" : "asjbdaknda"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "qwertyuiop@email.com", "password" : "password"})
    assert (r.status_code == 200) 
    
    resp = r.json()

    # valid name token and first and last 
    payload = {
        "token" : resp['token'],
        "name_first" : "fi38$# 29rst",
        "name_last" : "la1@0 9231st"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 200) 

    # logout
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    # invalid token 
    payload = {
        "token" : resp['token'],
        "name_first" : "first",
        "name_last" : "last"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 403)

    # invalid name first - empty 
    payload = {
        "token" : resp['token'],
        "name_first" : "",
        "name_last" : "last"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid name first - > 50 
    payload = {
        "token" : resp['token'],
        "name_first" : "asdfghjklfshgdjasdkasdlasda8721031209312sdassaudhasuidhah78324623864319023123daoijdaojsda",
        "name_last" : "last"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid name last - empty 
    payload = {
        "token" : resp['token'],
        "name_first" : "first",
        "name_last" : ""
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid name last - > 50 
    payload = {
        "token" : resp['token'],
        "name_first" : "first",
        "name_last" : "asdfghjklfshgdjasdkasdlasda8721031209312sdassaudhasuidhah78324623864319023123daoijdaojsda"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 400) 


# USER PROFILE SETEMAIL
def test_user_profile_set_email():
    clear_v1()
    # valid user 1
    payload = {
        "email" : "2893ry7gyedjkap@email.com",
        "password" : "password",
        "name_first" : "sjdnksand",
        "name_last" : "asjbdaknda"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "2893ry7gyedjkap@email.com", "password" : "password"})
    assert (r.status_code == 200) 

    resp = r.json()

    # valid email + token 
    payload = {
        "token" : resp['token'],
        "email" : "iajsdiofjsao@email.com"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/setemail/v1', json = payload)
    assert (r.status_code == 200) 

    # invalid email
    payload = {
        "token" : resp['token'],
        "email" : "asidjoas"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/setemail/v1', json = payload)
    assert (r.status_code == 400) 

    # logout
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)
    
    # invalid token 
    payload = {
        "token" : resp['token'],
        "email" : "ayguio92032@email.com"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/setemail/v1', json = payload)
    assert (r.status_code == 403) 


# USER PROFILE SET HANDLE 
def test_user_profile_set_handle():
    clear_v1()
    # valid user 1
    payload = {
        "email" : "zxcvbnm@email.com",
        "password" : "password",
        "name_first" : "12345",
        "name_last" : "asdfg"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "zxcvbnm@email.com", "password" : "password"})
    assert (r.status_code == 200) 

    # valid user 2
    payload = {
        "email" : "17481920@email.com",
        "password" : "password",
        "name_first" : "hello",
        "name_last" : "world"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "17481920@email.com", "password" : "password"})
    assert (r.status_code == 200) 

    resp = r.json()

    # duplicate handle 
    payload = {
        "token" : resp['token'],
        "handle_str" : "12345asdfg"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid handle - too short
    payload = {
        "token" : resp['token'],
        "handle_str" : "ab"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid handle - too long
    payload = {
        "token" : resp['token'],
        "handle_str" : "asdfghjkl456789039eiojhdvsbn27yueqwihsdajnklm"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 400) 

    # invalid handle - not alphanumeric
    payload = {
        "token" : resp['token'],
        "handle_str" : "!@2d*( hsfdui"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 400) 

    # valid handle
    payload = {
        "token" : resp['token'],
        "handle_str" : "newhandle"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 200) 

    # # invalid token 
    # payload = {
    #     "token" : resp['token'],
    #     "handle_str" : "a389urefijs"
    # } 

    # r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    # assert (r.status_code == 403) 

    
