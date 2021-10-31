from flask.globals import request
import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.auth import auth_register_v2, auth_logout_v1, auth_login_v2
from src.users import token_check, u_id_check

BASE_URL = 'http://127.0.0.1:3178'

# USERS ALL 
def test_users_all():

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

    # login without registering 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "2qioaj90wio@email.com", "password" : "password"})
    assert (r.status_code == 400)

    # logout  
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    # invalid token 
    invalid_token = resp['token']

    r = requests.get(f'{BASE_URL}/users/all/v1', params = {"token" : invalid_token})
    assert (r.status_code == 403)

def test_user_profile_valid():
    requests.delete(f'{BASE_URL}/clear/v1')

    payload = {
        "email" : "hjqbwsx@email.com",
        "password" : "password",
        "name_first" : "ehwjjskoo",
        "name_last" : "aishdufibjn"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    payload = {
        "email" : "asiudhjan@email.com",
        "password" : "password",
        "name_first" : "ehwjjskoo",
        "name_last" : "aishdufibjn"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)
    resp = r.json()

    assert resp['auth_user_id'] == 2

    # invalid token?????

    # valid token + valid id 
    payload = {
        "token" : resp['token'],
        "u_id" : resp['auth_user_id']
    } 
    
    r = requests.get(f'{BASE_URL}/user/profile/v1', params = payload)
    assert (r.status_code == 200) 

# USER PROFILE 
def test_user_profile():
    requests.delete(f'{BASE_URL}/clear/v1')
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
        "name_first" : "wriejof",
        "name_last" : "3qweldk"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)
    
    resp = r.json()

    # valid token + valid id 
    payload = {
        "token" : resp['token'],
        "u_id" : resp['auth_user_id']
    } 

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

# USER PROFILE SETNAME 
def test_user_profile_setname():
    requests.delete(f'{BASE_URL}/clear/v1')


    # valid user 1
    payload = {
        "email" : "qwertyuiop@email.com",
        "password" : "password",
        "name_first" : "firstfirst",
        "name_last" : "lastlast"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "qwertyuiop@email.com", "password" : "password"})
    assert (r.status_code == 200) 
    
    resp = r.json()

    # valid name token and first and last 
    payload = {
        "token" : resp['token'],
        "name_first" : "firstfirst",
        "name_last" : "lastlast"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/setname/v1', json = payload)
    assert (r.status_code == 200) 

    # logout
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    # invalid token 
    payload = {
        "token" : resp['token'],
        "name_first" : "firstfirst",
        "name_last" : "lastlast"
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
    requests.delete(f'{BASE_URL}/clear/v1')
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
    requests.delete(f'{BASE_URL}/clear/v1')
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
    resp = r.json()

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


    # valid user 3
    payload = {
        "email" : "by7guhjGVC0@email.com",
        "password" : "password",
        "name_first" : "hu8hjno",
        "name_last" : "world"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200) 
    resp = r.json()

    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    payload = {
        "token" : resp['token'],
        "handle_str" : "a389urefijs"
    } 

    # invalid token 
    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 403) 



    
