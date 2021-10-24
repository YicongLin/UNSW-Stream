import pytest
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import InputError, AccessError

# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        channels_create_v2(token, 'name', True)

def test_invalid_input():
    auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    with pytest.raises(InputError):
        channels_create_v2(token, '', False)
        channels_create_v2(token, 'abfbabbcabdkbrafbakbfkab', False)
        channels_create_v2(token, '', True)
        channels_create_v2(token, 'dfdsjhkjhsdshkjfkjsdfjhjksdf  ', True)

    
def test_channel_succesfully_created():
    auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']  
    channel_id = channels_create_v2(token, 'channel1', True)['channel_id']
    assert channels_list_v2(token) == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'channel1'
            }
        ]
    }
 

