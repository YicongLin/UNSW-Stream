import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:2000'

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

# First user creates a public channel
@pytest.fixture
def channel_one(register_first):
    token = register_first['token']
    payload = {
        "token": token,
        "name": "Channel one",
        "is_public": True
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
        "name": "Channel two",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    resp = r.json()
    return resp

# First user creates a DM with second user
@pytest.fixture
def dm_one(register_first, register_second):
    token = register_first['token']
    u_id = register_second['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp

# Second user creates a DM with first and third users
@pytest.fixture
def dm_two(register_first, register_second, register_third):
    token = register_second['token']
    u_id_1 = register_first['auth_user_id']
    u_id_3 = register_third['auth_user_id']
    payload = {
        "token": token,
        "u_ids": [u_id_1, u_id_3]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    resp = r.json()
    return resp

# ================================================
# =================== TESTS ======================
# ================================================

# Testing for invalid token
def test_invalid_token(clear_setup, register_first):
    # first user registers; obtain token
    token = register_first['token']
    # first user logs out; this invalidates the token
    requests.post(f'{BASE_URL}/auth/logout/v1', json = {"token": token})
    # first user gets notifications
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token})
    # this should raise an error message of "Invalid token"
    assert r.status_code == 403

# Testing that adding a user to a channel will notify the user
def test_added_to_channel(clear_setup, register_first, register_second, channel_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    u_id_2 = register_second['auth_user_id']
    # first user creates a public channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user invites second user to join
    payload = {
        "token": token_1,
        "channel_id": channel_id,
        "u_id": u_id_2
    }
    requests.post(f'{BASE_URL}/channel/invite/v2', json = payload)
    # test that the second user gets a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    assert r.status_code == 200
    notification = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "firstuser added you to Channel one"
    }
    response = r.json()
    assert response == {"notifications": [notification]}

# Testing that adding a user to a DM will notify the user
def test_added_to_dm(clear_setup, register_first, register_second, dm_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    u_id_2 = register_second['auth_user_id']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # test that the second user gets a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    assert r.status_code == 200
    # test the return value
    notification = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "firstuser added you to firstuser, seconduser"
    }
    response = r.json()
    assert response == {"notifications": [notification]}

# Testing that a member tagged in a channel will get notified;
# send one message that is under 20 characters long, and one message that is over 20 characters long
def test_member_tagged_in_channel(clear_setup, register_first, register_second, channel_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates a public channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user joins the channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user tags second user in a message (over 20 characters)
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "This is a message over 20 characters @seconduser"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # first user tags second user in another message (under 20 characters)
    payload3 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi @seconduser"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload3)
    # test the return value
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    notification1 = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "firstuser tagged you in Channel one: This is a message ov"
    }
    notification2 = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "firstuser tagged you in Channel one: Hi @seconduser"
    }
    response = r.json()
    assert response == {"notifications": [notification2, notification1]}

# Testing that a member tagged in a DM will get notified;
# send one message that is under 20 characters long, and one message that is over 20 characters long
def test_member_tagged_in_dm(clear_setup, register_first, register_second, dm_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # second user tags first user in a message (over 20 characters)
    payload1 = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "This is a message over 20 characters @firstuser"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user tags first user in another message (under 20 characters)
    payload2 = {
        "token": token_2,
        "dm_id": dm_id,
        "message": "Hi @firstuser"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload2)
    # test that the first user receives the notifications
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_1})
    notification1 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "seconduser tagged you in firstuser, seconduser: This is a message ov"
    }
    notification2 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "seconduser tagged you in firstuser, seconduser: Hi @firstuser"
    }
    response = r.json()
    assert response == {"notifications": [notification2, notification1]}

# Testing for a case where a user gets tagged in a channel they are not a member of;
# they should not receive any notifications
def test_not_member_tagged_in_channel(clear_setup, register_first, register_second, channel_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token
    token_2 = register_second['token']
    # first user creates a public channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # first user tags second user in a message 
    payload = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hello @seconduser"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # test the return value; the second user should not have any notifications
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    response = r.json()
    assert response == {"notifications": []}

# Testing for a case where a user gets tagged in a DM they are not a member of;
# they should not receive any notifications
def test_not_member_tagged_in_dm(clear_setup, register_first, register_third, dm_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # third user registers; obtain token
    token_3 = register_third['token']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user tags third user in a message 
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hello @thirduser"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # test the return value; the third user should not have any notifications
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_3})
    response = r.json()
    assert response == {"notifications": []}

# Testing for a case where multiple users get tagged in a channel;
# all users tagged should receive a notification
def test_multiple_tags_channel(clear_setup, register_first, register_second, register_third, channel_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token
    token_2 = register_second['token']
    # third user registers; obtain token
    token_3 = register_third['token']
    # first user creates a public channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second and third users join the channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    payload2 = {
        "token": token_3,
        "channel_id": channel_id,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload2)
    # first user tags second and third users in the same message 
    payload3 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "Hi guys @seconduser @thirduser"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload3)
    # test that the second and third users both receive a notification
    r1 = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    r2 = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_3})
    notification = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "firstuser tagged you in Channel one: Hi guys @seconduser "
    }
    response1 = r1.json()
    response2 = r2.json()
    assert response1 == response2 == {"notifications": [notification]} 

# Testing for a case where multiple users get tagged in a channel;
# all users tagged should receive a notification
def test_multiple_tags_dm(clear_setup, register_first, register_second, register_third, dm_two):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token
    token_2 = register_second['token']
    # third user registers; obtain token
    token_3 = register_third['token']
    # second user creates a DM with first and third users; obtain dm_id
    dm_id = dm_two['dm_id']
    # first user tags second and third users in the same message 
    payload = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "Hi guys @seconduser @thirduser"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # test that the second and third users both receive a notification
    r1 = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_2})
    r2 = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_3})
    notification1 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "first user added you to firstuser, seconduser, thirduser"
    }
    notification2 = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "firstuser tagged you in firstuser, seconduser: Hi guys @seconduser "
    }
    response1 = r1.json()
    response2 = r2.json()
    assert response1 == response2 == {"notifications": [notification2, notification1]} 

# Testing for a case where a message sent by a user in a channel gets a react;
# the user should receive a notification
def test_react_channel(clear_setup, register_first, register_second):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token
    token_2 = register_second['token']
    # first user creates a public channel; obtain channel_id
    channel_id = channel_one['channel_id']
    # second user joins the channel
    payload1 = {
        "token": token_2,
        "channel_id": channel_id,
    }
    requests.post(f'{BASE_URL}/channel/join/v2', json = payload1)
    # first user sends a message to the channel
    payload2 = {
        "token": token_1,
        "channel_id": channel_id,
        "message": "React to this"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload2)
    # second user reacts to the message
    payload3 = {
        "token": token_2,
        "message_id": 1,
        "react_id": 1
    }
    requests.post(f'{BASE_URL}/message/react/v1', json = payload3)
    # test that the first user receives a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_1})
    notification = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": "seconduser reacted to your message in Channel one"
    }
    response = r.json()
    assert response == {"notifications": [notification]}

# Testing for a case where a message sent by a user in a DM gets a react;
# the user should receive a notification
def test_react_dm(clear_setup, register_first, register_second, dm_one):
    # first user registers; obtain token
    token_1 = register_first['token']
    # second user registers; obtain token and u_id
    token_2 = register_second['token']
    # first user creates a DM with second user; obtain dm_id
    dm_id = dm_one['dm_id']
    # first user sends a message to the DM
    payload1 = {
        "token": token_1,
        "dm_id": dm_id,
        "message": "React to this"
    }
    requests.post(f'{BASE_URL}/message/senddm/v1', json = payload1)
    # second user reacts to the message
    payload2 = {
        "token": token_2,
        "message_id": 1,
        "react_id": 1
    }
    requests.post(f'{BASE_URL}/message/react/v1', json = payload2)
    # test that the first user receives a notification
    r = requests.get(f'{BASE_URL}/notifications/get/v1', params = {"token": token_1})
    notification = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": "seconduser reacted to your message in firstuser, seconduser"
    }
    response = r.json()
    assert response == {"notifications": [notification]}