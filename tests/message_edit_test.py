import pytest
import requests
import json
from src import config
from src.auth import auth_register_v2
from src.dm import dm_create_v1
from src.message import message_remove_v1

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

# Testing for invalid message length
def test_invalid_message_length(valid):
    token_1, _, _, _, dm_id_1, _ = valid
    payload = {
        "token": token_1,
        "dm_id": dm_id_1,
        "message": ""
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload)
    assert r.status_code == 400

    payload = {
       "token": token_1,
        "dm_id": dm_id_1,
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
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload)
    assert r.status_code == 400

# Testing for access error 
    def test_valid_access():
    token_1, _, _, _, dm_id_1, _ = valid
    payload = {
        "token": token_1,
        "dm_id": dm_id_1,
        "message": ""
    }
    r = requests.put(f'{BASE_URL}/message/edit/v1', json = payload)
    assert r.status_code == 400

