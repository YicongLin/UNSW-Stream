import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:3000'

def test_valid_one_user():
    resp = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    assert (resp.status_code == 200)

def test_valid_three_users():
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson2@email.com", "password": "password2", "name_first": "Test2", "name_last": "Person2"})
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson3@email.com", "password": "password3", "name_first": "Test3", "name_last": "Person3"})

def test_invalid_email():
    resp = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson", "password": "password", "name_first": "Test", "name_last": "Person"})
    assert (resp.status_code == 400)

    