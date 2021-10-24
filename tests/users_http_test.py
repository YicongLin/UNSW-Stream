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

    # invalid token 


    # valid token 
    resp = r.json()
    valid_token = resp['token']

    # response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "Ijks98ruwio@email.com", "password": "password"})
    # token_2 = json.loads(response.text)['token']

    r = requests.get(f'{BASE_URL}/users/all/v1', json = {valid_token})
    assert (r.status_code == 200)   


# USER PROFILE 

# invalid token 

# invalid uid 

# valid token 

# valid id 

# USER PROFILE SETNAME 

# invalid token 

# invalid name first 

# invalid name last 

# valid token 

# valid name first 

# valid name last 

# USER PROFILE SETEMAIL 
# invalid token 

# invalid email


# valid token 

# valid email 

# USER PROFILE SET HANDLE 

# invalid token 

# invalid handle

# valid token 

# valid handle 

