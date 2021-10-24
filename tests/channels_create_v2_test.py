import pytest
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2
from src.error import InputError

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
 

