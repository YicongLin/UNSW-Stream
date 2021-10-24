import pytest
from src.channels import channels_create_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.dm import dm_create_v1, dm_list_v1

# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_create_v1(token, [])

# create a dm of 2 people    
def test_dm_create():
    auth_register_v2("test@gmail.com", "password454643", "yicong", "lin")
    register_return = auth_register_v2("test1@gmail.com", "password454643", "kevin", "lin")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    
    token = login_return['token']
    u_id = register_return['auth_user_id']
    dm_id = dm_create_v1(token, [u_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['kevinlin', 'yiconglin']
            }
        ]
    }
    
def test_invalid_id():
    auth_register_v2("test90@gmail.com", "password454643", "long", "chen")
    dan_id = auth_register_v2("test40@gmail.com", "password454643", "dan", "lin")['auth_user_id']
    login_return = auth_login_v2("test90@gmail.com", "password454643")
    token = login_return['token']
    with pytest.raises(InputError):
        dm_create_v1(token, [-9])
        dm_create_v1(token, [-9, 10, -11])
        dm_create_v1(token, [dan_id, -1])