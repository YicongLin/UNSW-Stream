import pytest
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import AccessError
from src.dm import dm_create_v1, dm_list_v1

# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        channels_list_v2(token)

# test for a user that didn't join or create any channel
def test_empty_list():
    auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    assert channels_list_v2(token) == {
        'channels': [

        ]
    }
    
def test_list():
    auth_register_v2("testing@gmail.com", "passwordsdhhfd", 'james', 'wang')
    login_return = auth_login_v2("testing@gmail.com", "passwordsdhhfd")
    token = login_return['token']
    channel_id = channels_create_v2(token, 'channel1', False)['channel_id']
    assert channels_list_v2(token) == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'channel1'
            }
        ]
    }
