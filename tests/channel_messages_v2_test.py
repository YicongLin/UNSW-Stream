import json
from src import config
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens and channel IDs
@pytest.fixture
def valid():
    clear_v1()
    # tokens
    token_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['token']
    token_2 = auth_register_v2("asd@fgh.com", "password", "jkl", "asd")['token']

    # token_1 creates channel
    channel = channels_create_v2(token_1, "1", True)['channel_id']

    return token_1, token_2, channel

# Test for invalid channel_id
def test_invalid_channel_id(valid):
    token_1, *_ = valid
    payload = {
        "token": token_1,
        "channel_id": "invalid_id",
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

# Test for invalid token
def test_invalid_token(valid):
    _, _, channel = valid
    payload = {
        "token": "invalid token",
        "channel_id": channel,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

def test_invalid_start(valid):
    token_1, _, channel = valid
    payload = {
        "token": token_1,
        "channel_id": channel,
        "start": 2
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400



    
    # two users: one not a member of channel
    # send message, assert return type