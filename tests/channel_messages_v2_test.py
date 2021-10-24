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

# Testing for invalid channel_id
def test_invalid_channel_id(valid):
    token_1, *_ = valid
    payload = {
        "token": token_1,
        "channel_id": "invalid_id",
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

# Testing for invalid token
def test_invalid_token(valid):
    _, _, channel = valid
    payload = {
        "token": "invalid token",
        "channel_id": channel,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

# Testing for a case where start is greater than the total number of messages
def test_invalid_start(valid):
    token_1, _, channel = valid
    payload = {
        "token": token_1,
        "channel_id": channel,
        "start": 2
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

# Testing for a case where the authorised user is not a member of the channel
def test_not_a_member(valid):
    _, token_2, channel = valid
    payload = {
        "token": token_2,
        "channel_id": channel,
        "start": 2
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 400

# Testing valid case
def test_valid(valid):
    token_1, _, channel = valid
    payload = {
        "token": token_1,
        "channel_id": channel,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    assert r.status_code == 200

# Assert correct return
def test_correct_return(valid):
    token_1, _, channel = valid
    
    # token_1 sends a message to the channel;
    # the message will have message_id of 1
    payload1 = {
        "token": token_1,
        "channel_id": channel,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload1)

    # obtaining the time the message is created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # token_1 requests to return channel messages;
    # assert that the message with relevant information is returned
    payload = {
        "token": token_1,
        "channel_id": channel,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', json = payload)
    message = {
        'message_id': 1,
        'u_id': token_1,
        'message': 'Hello world',
        'time_created': time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": 50}
