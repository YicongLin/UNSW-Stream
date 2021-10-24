import pytest
from src.channels import channels_create_v2, channels_list_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1
from src.other import clear_v1

# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_remove_v1(token, dm_id)

# check if the token passed in is the creator of the dm, if not raise access error
def test_not_creator():
    
    auth_register_v2("test35@gmail.com", "password454643", "darren", "gao")
    auth_register_v2("test21@gmail.com", "password454643", "anthony", "huang")
    gao_login_return = auth_login_v2("test35@gmail.com", "password454643")
    huang_login_return = auth_login_v2("test21@gmail.com", "password454643")
    gao_token = gao_login_return['token']
    huang_token = huang_login_return['token']
    huang_id = huang_login_return['auth_user_id']
    dm_id = dm_create_v1(gao_token, [huang_id])['dm_id']

    with pytest.raises(AccessError):
        dm_remove_v1(huang_token, dm_id)

# if the dm id is not found in the dm datastore, raise input error
def test_invalid_dm():

    auth_register_v2("test53@gmail.com", "password454643", "amy", "chen")
    login_return = auth_login_v2("test53@gmail.com", "password454643")
    token = login_return['token']
    dm_create_v1(token, [])
    with pytest.raises(InputError):
        dm_remove_v1(token, -1)
        dm_remove_v1(token, 0)
        dm_remove_v1(token, -100)

# create a dm and remove, and try to list it out to see if it's empty
def test_remove_dm():
    
    anna_id = auth_register_v2("test99@gmail.com", "password454643", "anna", "li")['auth_user_id']
    auth_register_v2("test89@gmail.com", "password454643", "anne", "li")
    login_return = auth_login_v2("test89@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [anna_id])['dm_id']
    dm_remove_v1(token, dm_id)
    assert dm_list_v1(token) == {
        'dms': [

        ]
    }
