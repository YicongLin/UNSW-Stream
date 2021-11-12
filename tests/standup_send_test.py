from datetime import datetime, timezone
import math
from src.config import url
BASE_URL = url
import json
import requests

def test_invalid_token_message_send_later():
    requests.delete(f'{BASE_URL}/clear/v1')
    # a user register and login
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    
    # obtain token
    token = json.loads(response.text)['token']

    # create a channel
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']

    # log out
    response = requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token})
    assert (response.status_code) == 200

    # it should raise an access error
    response = requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token, "channel_id": channel_id, "message": "helloworld"})
    assert (response.status_code) == 403
    

def test_not_a_member():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # two users register
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login@gmail.com", "password": "password454643", "name_first": "tom", "name_last": "liu"})

    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "liu"})

    # both users logining in
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login@gmail.com", "password": "password454643"})
    token_fir = json.loads(response.text)['token']

    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login1@gmail.com", "password": "password454643"})
    token_sec = json.loads(response.text)['token']

    # second user create a channel
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token_sec, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']

    # first user try to send a message
    response = requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token_fir, "channel_id": channel_id, "message": "helloworld"})
    assert (response.status_code) == 403


def test_invalid_channel():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # user register
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "liu"})

    # user login and obtain token
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login1@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']

    # user create a channel
    requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})

    response = requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token, "channel_id": -1, "message": "helloworld"})
    assert (response.status_code) == 400


def test_invalid_message_length():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # user register
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "liu"})

    # user login and obtain token
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login1@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']

    # user create a channel
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']

    # user try to send a message with over 1000 characters
    payload = {
        "token": token, 
        "channel_id": channel_id, 
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
                    sit amet adipiscing sem neque sed ipsum. No "
    }

    response = requests.post(f'{BASE_URL}/standup/send/v1', json= payload)
    assert (response.status_code) == 400

