import pytest
from src.channels import channels_create_v2
from src.auth import auth_register_v2, auth_login_v2
from src.error import InputError
from src.dm import dm_create_v1, dm_list_v1
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