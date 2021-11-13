import pytest
import requests
import json
from src import config
import math
from datetime import datetime, timezone
from src.config import url

BASE_URL = url

# ================================================
# ================= FIXTURES =====================
# ================================================

# Clear data store
@pytest.fixture
def clear_setup():
    requests.delete(f'{BASE_URL}/clear/v1')

# Register first user
@pytest.fixture
def register_first():
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# Register second user
@pytest.fixture
def register_second():
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# Register third user
@pytest.fixture
def register_third():
    payload = {
        "email": "third@email.com", 
        "password": "password", 
        "name_first": "third", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    return resp

# First user creates a private channel
@pytest.fixture
def channel_one(register_first):
    token = register_first['token']
    payload = {
        "token": token,
        "name": "1",
        "is_public": False
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# Second user creates a public channel
@pytest.fixture
def channel_two(register_second):
    token = register_second['token']
    payload = {
        "token": token,
        "name": "2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid channel ID
def test_invalid_channel(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user invites second user to a channel with invalid ID
    payload = {
        "token": token,
        "channel_id": 5,
        "u_id": u_id
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    assert r.status_code == 400

# Testing for invalid u_id
def test_invalid_user(clear_setup, register_first, channel_one):
    # first user registers; obtain token
    token = register_first['token']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user invites user with invalid ID to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "u_id": 7
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    assert r.status_code == 400

# Testing for a case where u_id refers to a user 
# who is already a member of the channel
def test_already_a_member(clear_setup, register_first, register_second, channel_one, channel_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    u_id = register_first['auth_user_id']
    # second user registers; obtain token
    token_2 = register_second['token']
    # first user creates channel
    channel_one
    # second user creates public channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user joins channel
    payload = {
        "token": token_1,
        "channel_id": channel_id
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload)
    # second user attempts to invite first user
    payload = {
        "token": token_2,
        "channel_id": channel_id,
        "u_id": u_id
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    assert r.status_code == 400

# Testing for invalid token ID
def test_invalid_token(clear_setup, register_first, register_second, channel_one):
    # first user registers; obtain token
    token = register_first['token']
    # second user registers; obtain u_id
    u_id = register_second['auth_user_id']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user attempts to invite second user to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    assert r.status_code == 403

# Testing for a case where the authorised user is not a member of the valid channel
def test_not_a_member(clear_setup, register_first, register_third, channel_two):
    # first user registers; obtain token
    token = register_first['token']
    # third user registers; obtain u_id
    u_id = register_third['auth_user_id']
    # second user creates public channel; obtain channel_id
    channel_id = channel_two['channel_id']
    # first user attempts to invite third user to the channel
    payload = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    assert r.status_code == 403

def test_valid(clear_setup, register_first, register_second, channel_one, channel_two):
    # first user registers; obtain token and u_id
    token_1 = register_first['token']
    id_1 = register_first['auth_user_id']
    # second user registers; obtain u_id
    id_2 = register_second['auth_user_id']
    # first user creates channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user creates channel
    channel_two
    # first user invites second user to the channel
    payload1 = {
        "token": token_1,
        "channel_id": channel_id,
        "u_id": id_2
    }
    r = requests.post(f'{BASE_URL}/channel/invite/v2', json = payload1)
    assert r.status_code == 200
    # test that the second user has joined successfully;
    # first user requests channel details,
    # which should return a list of members including the second user
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
    }
    r = requests.get(f'{BASE_URL}/channel/details/v2', params = payload2)
    member1 = {
        "u_id": id_1,
        "email": "first@email.com",
        "name_first": "first",
        "name_last": "user",
        "handle_str": "firstuser"
    }
    member2 = {
        "u_id": id_2,
        "email": "second@email.com",
        "name_first": "second",
        "name_last": "user",
        "handle_str": "seconduser"
    }
    response = r.json()
    assert response == {"name": "1", "is_public": False, "owner_members": [member1], "all_members": [member1, member2]}





        
# # Testing for valid channel ID and u_id
# def test_valid(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_2)

# # Testing for a case where u_id refers to a user 
# # who is already a member of the channel
# def test_already_a_member(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_join_v1(id_2, channel_id_1)
#     with pytest.raises(InputError):
#         channel_invite_v1(id_1, channel_id_1, id_2)

# # Testing for a case where u_id refers to a user 
# # who is not already a member of the channel
# def test_not_already_a_member(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_2)
        
# # Testing for a case where the authorised user 
# # is not a member of the valid channel
# def test_not_a_member(valid_3_users):
#     id_1, _, id_3, _, channel_id_2 = valid_3_users
#     with pytest.raises(AccessError):
#         channel_invite_v1(id_1, channel_id_2, id_3)

# # Testing for a case where the authorised user 
# # is a member of the valid channel

# def test_member(valid_3_users):
#     id_1, _, id_3, channel_id_1, channel_id_2 = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_3)


# # Testing cases for other invalid input
# def test_empty():
#     with pytest.raises(InputError):
#         channel_invite_v1("", "", "")

# def test_invalid_strings():
#     with pytest.raises(InputError):
#         channel_invite_v1("invalid_id_1", "invalid_channel", "invalid_id_2")

# def test_symbols():
#     with pytest.raises(InputError):
#         channel_invite_v1("#&$_*%", "#$(%}(", "!@#$%^")

# def test_combination():
#     with pytest.raises(InputError):
#         channel_invite_v1("", "", "invalid_id_1")
#         channel_invite_v1("", "#$(%}(", "")
#         channel_invite_v1("invalid_id_1", "", "!@#$%^")
#         channel_invite_v1("invalid_id_1", "invalid_channel", "!@#$%^")
#         channel_invite_v1("#&$_*%", "", "!@#$%^")
#         channel_invite_v1("!@#$%^", "invalid_channel", "invalid_id_1")

