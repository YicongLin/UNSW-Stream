import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.dm import dm_create_v1

BASE_URL = 'http://127.0.0.1:8080'

# Creating valid tokens, DMs and user IDs
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
    # dms
    dm_id_1 = dm_create_v1(token_1, id_list_1)
    dm_id_2 = dm_create_v1(token_3, id_list_2)
    return token_1, token_2, token_3, id_1, dm_id_1, dm_id_2

# Testing for invalid dm_id
def test_invalid_dm_id(valid):
    token_1, _, _, _, _, _ = valid
    payload = {
        "token": token_1,
        "dm_id": "invalid_id",
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 400

# Testing for invalid token_id
def test_invalid_token_id(valid):
    token_1, _, _, _, _, _ = valid
    payload = {
        "token": "invalid_token_id",
        "dm_id": dm_id_1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 400

# Testing for valid message length
def test_valid_start():
    token_1, _, dm_id_1, _, start_0 = valid
    payload = {
        "token": token_1,
        "dm_id": dm_id_1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/dm/message/v1', json = payload)
    assert r.status_code == 200

# Testing all valid cases
def test_valid(valid):
    token_1, _, _, _, dm_id_1, _ = valid
    payload = {
        "token": token_1,
        "dm_id": dm_id_1,
        "message": "Hello World"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

    # Obtaining the time the message is created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # token_2 returns messages in dm_id_2
    payload = {
        "token": token_2,
        "dm_id": dm_id_2,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/dm/messages/v1', params = payload)
    assert r.status_code = 200
    message = {
        "message_id": 1,
        "u_id": id_1,
        "message": 'Hello world',
        "time_created": time_created
    }
    response = r.json()
    assert response == {"messages": [message], "start": 0, "end": 50}







# Testing cases for other invalid input
# def test_empty():
    with pytest.raises(InputError):
        dm_messages_v1("", "", 0)

#def test_invalid_strings():
 #   with pytest.raises(InputError):         
  #      dm_messages_v1("invalid_id_1", "dm", 1)

#def test_symbols():
 #   with pytest.raises(InputError):
  #      dm_messages_v1("#&$_*%", "#$(%}(", 1)

#def test_combination():
 #   with pytest.raises(InputError):
  #      dm_messages_v1("", "", 1)
   #     dm_messages_v1("", "#$(%}(", 1)
    #    dm_messages_v1("invalid_id_1", "", 1)
     #   dm_messages_v1("invalid_id_1", "invalid_dm", 1)
      #  dm_messages_v1("#&$_*%", "", 1)
       # dm_messages_v1("!@#$%^", "invalid_dm", 1)


 


