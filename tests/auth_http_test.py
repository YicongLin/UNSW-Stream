from flask.globals import request
import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.auth import auth_register_v2, auth_logout_v1, auth_login_v2
from src.users import token_check

BASE_URL = 'http://127.0.0.1:3178'

# AUTH REGISTER 
def test_auth_register():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # invalid email
    payload = {
        "email" : "invalid email",
        "password" : "password",
        "name_first" : "first",
        "name_last" : "last"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # invalid password - too little characters 
    payload = {
        "email" : "test@email.com",
        "password" : "123",
        "name_first" : "first",
        "name_last" : "last"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # invalid first name - too few letters
    payload = {
        "email" : "test@email.com",
        "password" : "password",
        "name_first" : "",
        "name_last" : "last"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # invalid first name - too many letters
    payload = {
        "email" : "test@email.com",
        "password" : "password",
        "name_first" : "qwertyuiopasdfghjklzxcvbnm1234567890qwertyuiopasdfghjklzxcvbnm",
        "name_last" : "last"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # invalid last name - too few letters 
    payload = {
        "email" : "test@email.com",
        "password" : "password",
        "name_first" : "first",
        "name_last" : ""
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # invalid last name - too many letters 
    payload = {
        "email" : "test@email.com",
        "password" : "password",
        "name_first" : "first",
        "name_last" : "qwertyuiopasdfghjklzxcvbnm1234567890qwertyuiopasdfghjklzxcvbnm"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # valid user 1
    payload = {
        "email" : "test1@email.com",
        "password" : "password1",
        "name_first" : "first1",
        "name_last" : "first1"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "test1@email.com", "password" : "password1"})
    assert (r.status_code == 200)
    
    # valid user 2
    payload = {
        "email" : "test2@email.com",
        "password" : "password2",
        "name_first" : "first1",
        "name_last" : "last1"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    # valid user 3
    payload = {
        "email" : "test3@email.com",
        "password" : "password3",
        "name_first" : "first1",
        "name_last" : "last1"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    # duplicate email 
    payload = {
        "email" : "test2@email.com",
        "password" : "password2",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 400)

    # handle over 20 characters - concatenate
    payload = {
        "email" : "test4@email.com",
        "password" : "password4",
        "name_first" : "thishandleistoolong",
        "name_last" : "thishandleistoolong"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    # only alphanumeric handles - should be cut out 
    payload = {
        "email" : "test5@email.com",
        "password" : "password5",
        "name_first" : "!@ 13#$%^& fir#st",
        "name_last" : "74%^ la#st"
    }

    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

# AUTH LOGIN 
def test_auth_login():
    requests.delete(f'{BASE_URL}/clear/v1')
    payload = {
        "email" : "testahudisjak@email.com",
        "password" : "password1",
        "name_first" : "first1",
        "name_last" : "last1"
    }

    # test unregistered email
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "testahudisjak@gmail.com", "password" : "password1"})
    assert (r.status_code == 400)

    # test invalid email 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "invalid email", "password" : "password"})
    assert (r.status_code == 400)

    # valid user 1
    payload = {
        "email" : "hfbasjkdnas@email.com",
        "password" : "password1",
        "name_first" : "first1",
        "name_last" : "last1"
    }

    # valid email + password 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "hfbasjkdnas@email.com", "password" : "password1"})
    assert (r.status_code == 200)

    # non-registered email 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "test3@email.com", "password" : "password2"})
    assert (r.status_code == 400)

    # valid user 2
    payload = {
        "email" : "thisisanothertest2@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }
    
    # correct password
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "thisisanothertest2@email.com", "password" : "password"})
    assert (r.status_code == 200)

    # incorrect password 
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "thisisanothertest2@email.com", "password" : "wrongpassword"})
    assert (r.status_code == 400)

# AUTH LOGOUT  
def test_auth_logout():
    requests.delete(f'{BASE_URL}/clear/v1')

    # valid user 1
    payload = {
        "email" : "randomemail@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    # register and login valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    resp = r.json()

    # logout
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp['token']})
    assert (r.status_code == 200)

    # login with invalid token 
    payload = {
        "token" : resp['token'],
        "handle_str" : "newhandle"
    } 
    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 403) 

    # valid user 2 
    payload = {
        "email" : "random2uy87uihemail@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    # register and login valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    resp_reg = r.json()

    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "random2uy87uihemail@email.com", "password" : "password"})
    assert (r.status_code == 200) 

    resp_log = r.json()

    # log out of reg account 
    r = requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": resp_reg['token']})
    assert (r.status_code == 200)

    # reg_token is invalid, log_token is valid 
    payload = {
        "token" : resp_log['token'],
        "handle_str" : "nijdoknle"
    } 

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 200) 

    # reg_token is invalid, log_token is valid 
    payload = {
        "token" : resp_reg['token'],
        "handle_str" : "289jab"
    }

    r = requests.put(f'{BASE_URL}/user/profile/sethandle/v1', json = payload)
    assert (r.status_code == 403) 

# AUTH DUPLICATE HANDLES
def test_duplicate_handles():
    requests.delete(f'{BASE_URL}/clear/v1')

    # valid user 1
    payload = {
        "email" : "randomemail@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    # register and login valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    # valid user 2
    payload = {
        "email" : "randomemailpt2@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    # register and login valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    # valid user 3
    payload = {
        "email" : "randomemailpt3@email.com",
        "password" : "password",
        "name_first" : "first2",
        "name_last" : "last2"
    }

    # register and login valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    



