import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.token_helpers import decode_JWT
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1
from src.other import clear_v1

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens and ids and a valid channel and dm
@pytest.fixture
def valid():
    clear_v1()
    # tokens
    token_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['token']
    token_2 = auth_register_v2("asd@fgh.com", "password", "jkl", "asd")['token']
    token_3 = auth_register_v2("abc@def.com", "password", "ghi", "jkl")['token']

    # token_1: id_1 
    # global owner
    decoded_token = decode_JWT(token_1)
    id_1 = decoded_token['u_id']

    # token_2: id_2
    # not a global owner
    decoded_token = decode_JWT(token_2)
    id_2 = decoded_token['u_id']

    # token_3: id_3
    # recipient of u_id's dm
    decoded_token = decode_JWT(token_3)
    id_3 = decoded_token['u_id']
    id_list = [id_3]

    # token_2 creates channel
    channel = channels_create_v2(token_2, "1", True)['channel_id']

    # token_2 creates dm with id_3
    dm = dm_create_v1(token_2, id_list)['dm_id']

    return token_1, token_2, token_3, id_1, id_2, id_3, channel, dm

# Testing for invalid u_id
def test_invalid_u_id(valid):
    token_1, *_ = valid
    payload = {
        "token": token_1,
        "u_id": "invalid id"
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(valid):
    _, _, _, id_1, *_ = valid
    payload = {
        "token": "invalid token",
        "u_id": id_1
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where the authorised user is not a global owner
def test_not_global_owner(valid):
    _, token_2, _, _, id_3, *_ = valid
    payload = {
        "token": token_2,
        "u_id": id_3
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 403

# Testing for a case where u_id is the only global owner
def test_only_global_owner(valid):
    token_1, _, _, id_1, *_ = valid
    payload = {
        "token": token_1,
        "u_id": id_1
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 400

# Test valid case
def test_valid(valid):
    token_1, _, _, _, id_2, *_ = valid
    payload = {
        "token": token_1,
        "u_id": id_2
    }
    r = requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload)
    assert r.status_code == 200

# Test user removal from channel members list, as well as removal of messages
def test_all_removed_from_channel(valid):
    token_1, _, token_3, id_1, id_2, id_3, channel, _ = valid

    # token_3 joins channel
    payload1 = {
        "token": token_3,
        "channel_id": channel
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)

    # token_2 sends a message to the channel
    payload2 = {
        "token": token_2,
        "channel_id": channel,
        "message": "Bye"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)

    # obtaining the time the message is created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # id_2 is removed from Streams
    payload3 = {
        "token": token_1,
        "u_id": id_2
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload3)

    # assert that id_2 is gone from channel;
    # token_3 requests channel details - id_2 will not be included in the list of members
    r = requests.get(f'{BASE_URL}/channel/details/v2', json = payload1)
    member = {
        "u_id": id_3,
        "email": "abc@def.com",
        "name_first": "ghi",
        "name_last": "jkl",
        "handle_str": "ghijkl"
    }
    response = r.json()
    assert response == {"name": "1", "is_public": True, "owner_members": [], "all_members": [member]}

    # assert the sent message is removed;
    # id_3 requests channel messages - the message will be replace with "Removed user"
    payload4 - {
        "token": token_3,
        "channel_id": channel,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload4)
    message = {
        "message_id": 1,
        "u_id": id_2,
        "message": "Removed user",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": 50}

# Test user removal from dm members list, as well as removal of messages
def test_all_removed_from_dm(valid):
    token_1, _, token_3, id_1, id_2, id_3, _, dm = valid

    # token_2 sends a message to the dm
    payload1 = {
        "token": token_2,
        "dm_id": dm,
        "message": "Bye"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)

    # obtaining the time the message is created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # id_2 is removed from Streams
    payload2 = {
        "token": token_1,
        "u_id": id_2
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload2)

    # assert that id_2 is gone from dm;
    # token_3 requests dm details - id_2 will not be included in the list of members
    payload3 = {
        "token": token_3,
        "dm_id": dm
    }
    r = requests.get(f'{BASE_URL}/dm/details/v1', json = payload3)
    user = {
        "u_id": id_3,
        "email": "abc@def.com",
        "name_first": "ghi",
        "name_last": "jkl",
        "handle_str": "ghijkl"
    }
    response = r.json()
    assert response == {"name": "1", "is_public": True, "owner_members": [], "all_members": [user]}

    # assert the sent message is removed;
    # id_3 requests dm messages - the message will be replaced with "Removed user"

    payload4 - {
        "token": token_3,
        "dm_id": dm,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', json = payload4)
    message = {
        "message_id": 1,
        "u_id": id_2,
        "message": "Removed",
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": 50}

# Test user removal from user list, but still also retrievable with user/profile
def test_user_list_and_profile(valid):
    token_1, _, _, id_1, id_2, id_3, *_ = valid

    # id_2 and id_3 are removed from Streams
    payload1 = {
        "token": token_1,
        "u_id": id_2
    }
    payload2 = {
        "token": token_1,
        "u_id": id_3
    }
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload1)
    requests.delete(f'{BASE_URL}/admin/user/remove/v1', json = payload2)

    # assert that id_2 and id_3 are gone from the list;
    # id_1 requests user list - only id_1 should remain
    r = requests.get(f'{BASE_URL}/users/all/v1', json = {"token": token_1})
    user = {
        "u_id": id_1,
        "email": qwe@rty.com,
        "name_first": "uio",
        "name_last": "qwe",
        "handle_str": "uioqwe"
    }
    response = r.json()
    assert response == {"users": [user]}

    # assert that the deleted user should still be retrievable with user/profile;
    # id_1 requests id_2's profile
    r = requests.get(f'{BASE_URL}/users/profile/v1', json = payload1)
    user = {
        "u_id": id_2,
        "email": '',
        "name_first": 'Removed',
        "name_last": 'user',
        "handle_str": ''
    }
    response = r.json()
    assert response == {"user": user}

