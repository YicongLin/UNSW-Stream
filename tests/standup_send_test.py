from datetime import datetime, timezone
import math
from src.config import url
BASE_URL = url
import json
import requests
import time
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

def test_standup_inactive():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # user register
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "liu"})

    # user login and obtain token
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login1@gmail.com", "password": "password454643"})
    token = json.loads(response.text)['token']

    # user create a channel
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']

    response = requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token, "channel_id": channel_id, "message": "helloworld"})
    assert (response.status_code) == 400

def test_valid_stand_up():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # user register
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login1@gmail.com", "password": "password454643", "name_first": "kevin", "name_last": "lin"})
    requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "login2@gmail.com", "password": "password454643", "name_first": "kang", "name_last": "liu"})
    # user login and obtain token
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login1@gmail.com", "password": "password454643"})
    token1 = json.loads(response.text)['token']
    u_id1 = json.loads(response.text)['auth_user_id']


    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "login2@gmail.com", "password": "password454643"})
    token2 = json.loads(response.text)['token']
    u_id2 = json.loads(response.text)['auth_user_id']

    # user create a channel
    create_return = requests.post(f'{BASE_URL}/channels/create/v2', json={"token": token1, "name": "channel1", "is_public": True})
    channel_id = json.loads(create_return.text)['channel_id']

    requests.post(f'{BASE_URL}/channel/invite/v2', json = {"token": token1, "channel_id": channel_id, "u_id": u_id2})
    requests.post(f'{BASE_URL}/standup/start/v1', json={"token": token1, "channel_id": channel_id, "length": 3})

    active_return = requests.get(f'{BASE_URL}/standup/active/v1', params={"token": token1, "channel_id": channel_id})
    time_finish = json.loads(active_return.text)['time_finish']

    response = requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token1, "channel_id": channel_id, "message": "hello"})
    assert (response.status_code) == 200

    requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token2, "channel_id": channel_id, "message": "world"})
    assert (response.status_code) == 200
    
    requests.post(f'{BASE_URL}/standup/send/v1', json={"token": token2, "channel_id": channel_id, "message": "12345"})
    assert (response.status_code) == 200
    
    
    time_now = datetime.now()
    time_created = math.floor(time_now.replace(tzinfo=timezone.utc).timestamp()) - 39600
    waiting_time = time_finish - time_created
    time.sleep(waiting_time)

    time_now = datetime.now()
    time_created = math.floor(time_now.replace(tzinfo=timezone.utc).timestamp()) - 39600
    payload = {
        "token": token1,
        "channel_id": channel_id,
        "start": 0
    }
    r = requests.get(f'{BASE_URL}/channel/messages/v2', params = payload)
    message = {
        "message_id": 1,
        "u_id": u_id1,
        "message": "kevinlin: hello\nkangliu: world\nkangliu: 12345",
        "time_created": time_created,
        "reacts": [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        "is_pinned": False
    }
    
    assert json.loads(r.text) == {"messages": [message], "start": 0, "end": -1}
    

    