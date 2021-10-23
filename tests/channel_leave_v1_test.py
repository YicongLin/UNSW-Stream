import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:8080'

# Testing for invalid channel ID
def test_invalid_channel(valid_3_users):
    requests.delete(f'{BASE_URL}/clear/v1')
    # Create two users
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "abc@email.com", "password": "abc", "Firstname": "abc", "Lastname": "def"})
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "def@email.com", "password": "def", "Firstname": "def", "Lastname": "ghi"})
    # First user logs in, creates a channel 
    requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "abc@email.com", "password": "abc"})
    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": "token_one", "name": "channel1", "is_public": True})
    # Error; second user trying to leave the channel they are not a member of
    response = requests.post(f'{BASE_URL}/channel/leave/v1', json={"token": "token_two", "channel_id": 1})
    assert (response.status_code == 400)
    # Error; invalid channel
    response = requests.post(f'{BASE_URL}/channel/leave/v1', json={"token": "token_two", "channel_id": "invalid"})
    assert (response.status_code == 400)


