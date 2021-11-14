import pytest 
import requests
from datetime import datetime, timezone
import math
from src.config import url 

BASE_URL = url 

def test_user_channel():
    requests.delete(f'{BASE_URL}/clear/v1')

    # register user1 with valid token 
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    token1 = resp['token']

    # call user stats 
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    resp = r.json()

    # assert involvement rate = 0 
    assert r.status_code == 200 
    assert resp['user_stats']['involvement_rate'] == 0

    # user1 creates & joins public channel 1
    payload = {
        "token": token1,
        "name": "channel1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_one_id = resp['channel_id']

    # user1 creates & joins public channel 2
    payload = {
        "token": token1,
        "name": "channel2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_two_id = resp['channel_id']

    # first user sends first message to channel1
    payload = {
        "token": token1,
        "channel_id": channel_one_id,
        "message": "first message to channel1"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

    # first user sends first message to channel2
    payload = {
        "token": token1,
        "channel_id": channel_two_id,
        "message": "first message to channel2"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

    # assert involvement rate = 4/4 
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 1

    # register user2 with valid token 
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    token2 = resp['token']

    # user2 creates & joins public channel 3
    payload = {
        "token": token2,
        "name": "channel3",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()

    # assert involvement rate = 4/5
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 0.8

    # user 1 removes message 
    payload = {
        "token": token1,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 200 

    # assert involvement rate = (2 + 0 + 2)/(3 + 0 + 1)
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 1

def test_user_dm_channel():
    requests.delete(f'{BASE_URL}/clear/v1')

    # register user1 with valid token 
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    token1 = resp['token']

    # register user2 with valid token 
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    token2 = resp['token']
    u_id2 = resp['auth_user_id']

    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 0

    # create dm with user1 and user2 
    payload = {
        "token" : token1,
        "u_ids" : [u_id2]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    dm1_id = resp['dm_id']

    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 1

    # user1 sends 1st message to dm1 
    payload = {
        "token": token1,
        "dm_id": dm1_id,
        "message": "user1 1st message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

    # user1 sends 2nd message to dm1 
    payload = {
        "token": token1,
        "dm_id": dm1_id,
        "message": "user1 2nd message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 1

    # user2 sends 1st message to dm1 
    payload = {
        "token": token2,
        "dm_id": dm1_id,
        "message": "user2 1st message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

    # assert involvement rate = (0 + 1 + 1)/(0 + 1 + 3)
    payload = {
        "token" : token2
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 0.50

    # user 1 removes message 
    payload = {
        "token": token1,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    assert r.status_code == 200 

    # assert involvement rate = (0 + 1 + 2)/(0 + 1 + 2)
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['involvement_rate'] == 1

    # user1 creates & joins public channel 1
    payload = {
        "token": token1,
        "name": "channel1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_one_id = resp['channel_id']

    # user2 creates & joins public channel 2
    payload = {
        "token": token2,
        "name": "channel2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_two_id = resp['channel_id']

    # second user sends first message to channel2
    payload = {
        "token": token2,
        "channel_id": channel_one_id,
        "message": "first message to channel2"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

    # second user sends second message to channel2
    payload = {
        "token": token2,
        "channel_id": channel_two_id,
        "message": "second message to channel2"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    # assert involvement rate = (1 + 1 + 2)/(1 + 1 + 4)
    assert resp['user_stats']['involvement_rate'] == 2/3

def test_user_timestamps():
    requests.delete(f'{BASE_URL}/clear/v1')

    # register user1
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    token1 = resp['token']

    # get time 
    time = datetime.now()
    user1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # register user2 
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    u_id2 = resp['auth_user_id']

    # user1 creates & joins public channel 1
    payload = {
        "token": token1,
        "name": "channel1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_one_id = resp['channel_id']

    # get time 
    time = datetime.now()
    channel1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # user1 creates & joins public channel 2
    payload = {
        "token": token1,
        "name": "channel2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    channel_one_id = resp['channel_id']

    # get time 
    time = datetime.now()
    channel2_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # create dm with user1 and user2 
    payload = {
        "token" : token1,
        "u_ids" : [u_id2]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    assert r.status_code == 200 
    resp = r.json()
    dm1_id = resp['dm_id']

    # get time 
    time = datetime.now()
    dm1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # user1 sends 1st message to dm1 
    payload = {
        "token": token1,
        "dm_id": dm1_id,
        "message": "user1 1st message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200

    # get time 
    time = datetime.now()
    message1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # user1 sends message 2 to channel 
    payload = {
        "token": token1,
        "channel_id": channel_one_id,
        "message": "first message to channel1"
    }
    requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    assert r.status_code == 200

    # get time 
    time = datetime.now()
    message2_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # CALL DM REMOVE 

    # checking timestamps 
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/user/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    assert resp['user_stats']['channels_joined'] == [
        {
        'num_channels_joined' : 0, 
        'time_stamp' : user1_time
        },
        {
        'num_channels_joined' : 1, 
        'time_stamp' : channel1_time
        },
        {
        'num_channels_joined' : 2, 
        'time_stamp' : channel2_time
        }
    ]
    assert resp['user_stats']['dms_joined'] == [
        {
        'num_dms_joined' : 0, 
        'time_stamp' : user1_time
        },
        {
        'num_dms_joined' : 1, 
        'time_stamp' : dm1_time
        }
    ]
    assert resp['user_stats']['messages_sent'] == [
        {
        'num_messages_sent' : 0, 
        'time_stamp' : user1_time
        }, 
        {
        'num_messages_sent' : 1, 
        'time_stamp' : message1_time
        },
        {
        'num_messages_sent' : 2, 
        'time_stamp' : message2_time
        }
    ]

def test_users_stats_utilization():
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # register user1 
    payload = {
        "email": "first@email.com", 
        "password": "password", 
        "name_first": "first", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    # get time 
    time = datetime.now()
    user1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    resp = r.json()
    token1 = resp['token']

    # register user2
    payload = {
        "email": "second@email.com", 
        "password": "password", 
        "name_first": "second", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()
    u_id2 = resp['auth_user_id']

    # user1 creates & joins public channel 1
    payload = {
        "token": token1,
        "name": "channel1",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    # get time 
    time = datetime.now()
    channel1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200 
    resp = r.json()
    channel_one_id = resp['channel_id']

    # user1 creates & joins public channel 2
    payload = {
        "token": token1,
        "name": "channel2",
        "is_public": True
    }
    r = requests.post(f'{BASE_URL}/channels/create/v2', json = payload)
    # get time 
    time = datetime.now()
    channel2_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200 
    resp = r.json()

    # create dm with user1 and user2 
    payload = {
        "token" : token1,
        "u_ids" : [u_id2]
    }
    r = requests.post(f'{BASE_URL}/dm/create/v1', json = payload)
    # get time 
    time = datetime.now()
    dm1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200 
    resp = r.json()
    dm1_id = resp['dm_id']

    # register user3 
    payload = {
        "email": "third@email.com", 
        "password": "password", 
        "name_first": "third", 
        "name_last": "user"
        }
    r = requests.post(f'{BASE_URL}/auth/register/v2', json = payload)
    resp = r.json()

    # assert utilization rate 
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/users/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()
    # assert utilization_rate == 2/3
    assert resp['workspace_stats']['utilization_rate'] == 2/3

    # user 1 sends message to channel 1 
    payload = {
        "token": token1,
        "channel_id": channel_one_id,
        "message": "first message to channel1"
    }
    r = requests.post(f'{BASE_URL}/message/send/v1', json = payload)
    # get time 
    time = datetime.now()
    message1_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200

    # user 1 sends message to dm
    payload = {
        "token": token1,
        "dm_id": dm1_id,
        "message": "user1 1st message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    assert r.status_code == 200
    # get time 
    time = datetime.now()
    message2_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
     
    # user 1 sends message to dm 
    payload = {
        "token": token1,
        "dm_id": dm1_id,
        "message": "user1 2nd message to dm1"
    }
    r = requests.post(f'{BASE_URL}/message/senddm/v1', json = payload)
    # get time 
    time = datetime.now()
    message3_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200

    # user 1 removes message 1 
    payload = {
        "token": token1,
        "message_id": 1
    }
    r = requests.delete(f'{BASE_URL}/message/remove/v1', json = payload)
    # get time 
    time = datetime.now()
    message4_time = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    assert r.status_code == 200 

    # assert timestamps are correct 
    payload = {
        "token" : token1
    }
    r = requests.get(f'{BASE_URL}/users/stats/v1', params = payload)
    assert r.status_code == 200 
    resp = r.json()

    assert resp['workspace_stats']['channels_exist'] == [
        {
            'num_channels_exist' : 0,
            'time_stamp' : user1_time 
        },
        {
            'num_channels_exist' : 1,
            'time_stamp' : channel1_time
        },
        {
            'num_channels_exist' : 2,
            'time_stamp' : channel2_time
        }]

    assert resp['workspace_stats']['dms_exist'] == [
        {
            'num_dms_exist' : 0, 
            'time_stamp' : user1_time
        },
        {
            'num_dms_exist' : 1, 
            'time_stamp' : dm1_time
        }]   
    
    assert resp['workspace_stats']['messages_exist'] == [
        {
            'num_messages_exist' : 0, 
            'time_stamp' : user1_time
        }, 
        {
            'num_messages_exist' : 1, 
            'time_stamp' : message1_time 
        },
        {
            'num_messages_exist' : 2, 
            'time_stamp' : message2_time 
        },
        {
            'num_messages_exist' : 3, 
            'time_stamp' : message3_time  
        },
        {
            'num_messages_exist' : 2, 
            'time_stamp' : message4_time  
        }]