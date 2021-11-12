from flask.globals import request
import pytest
import requests
import json
from src import config
from src.config import url

BASE_URL = url

# test whether email is sent 
def test_email_sent():
    requests.delete(f'{BASE_URL}/clear/v1')

    # user 1 
    payload = {
        "email" : "fakeemail@email.com",
        "password" : "password",
        "name_first" : "first",
        "name_last" : "last"
    }

    # register valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)
    r = requests.post(f'{BASE_URL}/auth/login/v2', json = {"email": "fakeemail@email.com", "password" : "password"})
    assert (r.status_code == 200)

    # user 2
    payload = {
        "email" : "afake@email.com",
        "password" : "password",
        "name_first" : "first1",
        "name_last" : "last1"
    }

    # register valid user 
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    assert (r.status_code == 200)

    payload = {
        "email" : "fakeemail@email.com"
    }
    
    # send reset password email 
    r = requests.post(f'{BASE_URL}/auth/passwordreset/request/v1', json = payload)
    assert (r.status_code == 200)

    # all active tokens from that account should be logged out 
    







