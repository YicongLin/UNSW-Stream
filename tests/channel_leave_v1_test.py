import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2
from src.other import clear_v1

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens and channel IDs
@pytest.fixture
def valid():
    clear_v1()
    # tokens
    token_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['token']
    token_2 = auth_register_v2("asd@fgh.com", "password", "jkl", "asd")['token']
    id_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['auth_user_id']
    # channels
    channel_1 = channels_create_v2(token_1, "1", True)['channel_id']
    return token_1, token_2, id_1, channel_1

# Testing for invalid channel ID
def test_invalid_channel(valid):
    token_1, _, _, _ = valid
    payload = {
        "token": token_1,
        "channel_id": "invalid_id"
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(valid):
    _, _, _, channel_1 = valid
    payload = {
        "token": "invalid_id",
        "channel_id": channel_1
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where the user is not a member of the channel
def test_not_a_member(valid):
    _, token_2, _, channel_1 = valid
    payload = {
        "token": token_2,
        "channel_id": channel_1
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 403

# Testing valid case
def test_valid(valid):
    token_1, _, _, channel_1 = valid
    payload = {
        "token": token_1,
        "channel_id": channel_1
    }
    r = requests.post(f'{BASE_URL}/channel/leave/v1', json = payload)
    assert r.status_code == 200

# Ensuring the user is gone from the list of channels after leaving
def test_user_left(valid):
    token_1, _, id_1, channel_1 = valid
    
    # token_2 joins channel_1
    payload1 = {
        "token": token_2,
        "channel_id": channel_1
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)

    # token_1 leaves channel_1
    payload2 = {
        "token": token_1,
        "channel_id": channel_1
    }
    requests.post(f'{BASE_URL}/channel/leave/v1', json = payload2)

    # token_2 returns channel_1 details
    r = requests.get(f'{BASE_URL}/channel/details/v2', json = payload1)
    member = {
        "u_id": id_1,
        "email": "qwe@rty.com",
        "name_first": "uio",
        "name_last": "qwe",
        "handle_str": "uioqwe"
    }
    response = r.json()
    assert response == {"name": "1", "is_public": True, "owner_members": [], "all_members": [member]}
