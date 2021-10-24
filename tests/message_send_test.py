import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.message import message_send_v1
from src.channel import channel_create_v2

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens, channels and user IDs
@pytest.fixture
def valid():
    clear_v1()
    # tokens
    token_1 = auth_register_v2("qwe@rty.com", "password", "uio", "qwe")['token']
    token_2 = auth_register_v2("asd@fgh.com", "password", "jkl", "asd")['token']
    token_3 = auth_register_v2("abc@gmail.com", "password", "abc", "def")['token']
    # id and id lists
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token_1, SECRET, algorithms=['HS256'])
    id_1 = decode_token['u_id']
    decode_token = jwt.decode(token_2, SECRET, algorithms=['HS256'])
    id_2 = decode_token['u_id']
    id_list_1 = [id_2]
    id_list_2 = [id_1, id_2]
    # channels
    channel_id_1 = channel_create_v2(token_1, id_list_1)
    channel_id_2 = channel_create_v2(token_3, id_list_2)
    return token_1, token_2, token_3, id_1, channel_id_1, channel_id_2

# Testing for invalid channel_id
def test_invalid_channel_id(valid):
    token_1, _, _, _, _, _ = valid
    payload = {
        "token": token_1,
        "channel_id": "invalid_id",
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token_id
def test_invalid_token_id(valid):
    token_1, _, _, _, _, _ = valid
    payload = {
        "token": "invalid_token_id",
        "channel_id": channel_id_1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid message length
def test_invalid_message_length(valid):
    token_1, _, _, _, channel_id_1, _ = valid
    payload = {
        "token": token_1,
        "channel_id": channel_id_1,
        "message": ""
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 400

    payload = {
       "token": token_1,
        "channel_id": channel_id_1,
        "message": "Lorem ipsum dolor sit amet, \
                    consectetuer adipiscing elit. Aenean commodo \
                    ligula eget dolor. Aenean massa. Cum sociis \
                    natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. \
                    Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat \
                    massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. \
                    In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu \
                    pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. \
                    Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, \
                    eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus.\
                    Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. \
                    Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. \
                    Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, \
                    sit amet adipiscing sem neque sed ipsum." 
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 400

# Testing all valid cases
def test_valid(valid):
    token_1, _, _, _, channel_id_1, _ = valid
    payload = {
        "token": token_1,
        "channel_id": channel_id_1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

# Testing to ensure the message was sent to the specified channel
def test_sent_messages(valid):
    token_1, token_2, _, id_1, _, channel_id_2 = valid
    # token_1 sends a message to channel_id_2
    payload = {
        "token": token_1,
        "channel_id": channel_id_2,
        "message": "Hello World"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)

    # Obtaining the time the message is created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # token_2 returns messages in channel_id_2
    payload = {
        "token": token_2,
        "channel_id": channel_id_2,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    assert r.status_code = 200
    message = {
        "message_id": 1,
        "u_id": id_1,
        "message": 'Hello world',
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": 50}








    
  



