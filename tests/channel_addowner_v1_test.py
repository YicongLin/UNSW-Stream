import pytest
import requests
import json
from src import config

# Need to be transmitted to http

# @pytest.fixture
# def create_users():
#     clear_v1()
#     valid_id_1 = auth_register_v1("testperson@email.com", "password", "Test", "Person")['auth_user_id']
#     valid_id_2 = auth_register_v1("testpersontwo@email.com", "passwordtwo", "Testtwo", "Persontwo")['auth_user_id']
#     valid_id_3 = auth_register_v1("testpersonthr@email.com", "passwordthr", "Testthr", "Personthr")['auth_user_id']
#     valid_id_4 = auth_register_v1("testpersonfour@email.com", "passwordfour", "Testfour", "Personfour")['auth_user_id']
#     valid_id = [valid_id_1, valid_id_2, valid_id_3, valid_id_4] # store valid user id for return multiple valid id
#     return valid_id

# #  Invalid channel_id and u_id
# def test_invalid_channelid_uid():
#     clear_v1()
#     resp = requests.post('http://127.0.0.1:8080/channel/addowner/v1', json={'token': 'hello', 'channel_id': 123, 'u_id': 1})
#     assert (resp.status_code == 400)

# #  Invalid channel_id
# def test_invalid_channelid(create_users):
#     clear_v1()
#     valid_id_1 = create_users[0]
#     resp = requests.post('http://127.0.0.1:8080/channel/addowner/v1', json={'token': 'hello', 'channel_id': 123, 'u_id': valid_id_1})
#     assert (resp.status_code == 400)

# #  Invalid u_id
# def test_invalid_uid(create_users):
#     clear_v1()
#     valid_id_1 = create_users[0]
#     valid_channel_id = channels_create_v1(valid_id_1, 'cse', True)["channel_id"] 
#     resp = requests.post('http://127.0.0.1:8080/channel/addowner/v1', json={'token': 'hello', 'channel_id': 123, 'u_id': 1})
#     assert (resp.status_code == 400)

# User is not a member of channel
# def test_not_member(create_users):
#     clear_v1()
#     valid_id_1 = create_users[0]
#     valid_id_2 = create_users[1]
#     valid_id_3 = create_users[2]
#     valid_channel_id = channels_create_v1(valid_id_1, 'cse', True)["channel_id"] # create a channel
#     channel_join_v1(valid_id_2, valid_channel_id)
#     channel_invite_v1(valid_id_2, valid_channel_id, valid_id_3)
#     resp = requests.post('http://127.0.0.1:8080/channel/addowner/v1', json={'token': 'hello', 'channel_id': 123, 'u_id': 1})
#     assert (resp.status_code == 400)

# User already is an owner


# No permissions to add owner
# Check token and owner_members




