import pytest
from src.channels import channels_create_v2
from src.auth import auth_logout_v1, auth_register_v2, auth_login_v2
from src.error import AccessError
from src.dm import dm_create_v1, dm_list_v1
# checking for invalid token, if a user is logged out that token is invalid
def test_valid_token():
    auth_register_v2("login@gmail.com", "password454643", "tom", "liu")
    login_return = auth_login_v2("login@gmail.com", "password454643")
    token = login_return['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        dm_list_v1(token)

# only the creator is in the dm
def test_list_only_creator():
    auth_register_v2("test@gmail.com", "password454643", "john", "smith")
    login_return = auth_login_v2("test@gmail.com", "password454643")
    token = login_return['token']
    
    dm_id = dm_create_v1(token, [])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['johnsmith']
            }
        ]
    }
# a dm of 5 people
def test_list():
    auth_register_v2("test1@gmail.com", "password454643", "yicong", "lin")
    zami_id = auth_register_v2("test3@gmail.com", "password454643", "zami", "lee")['auth_user_id']
    lilian_id = auth_register_v2("test4@gmail.com", "password454643", "lilian", "pok")['auth_user_id']
    kang_id = auth_register_v2("test2@gmail.com", "password454643", "kang", "liu")['auth_user_id']
    prasannaa_id = auth_register_v2("test5@gmail.com", "password454643", "prasannaa", "pandey")['auth_user_id']


    login_return = auth_login_v2("test1@gmail.com", "password454643")
    token = login_return['token']
    dm_id = dm_create_v1(token, [kang_id, zami_id, lilian_id, prasannaa_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['kangliu', 'lilianpok', 'prasannaapandey', 'yiconglin', 'zamilee']
            }
        ]
    }

def test_list1():
    auth_register_v2("testa@gmail.com", "password454643", "jike", "zhang")
    long_id = auth_register_v2("testb@gmail.com", "password454643", "long", "ma")['auth_user_id']
    xin_id = auth_register_v2("testc@gmail.com", "password454643", "xin", "xu")['auth_user_id']
    login_return = auth_login_v2("testa@gmail.com", "password454643")
    token = login_return['token']

    dm_id = dm_create_v1(token, [long_id, xin_id])['dm_id']
    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['jikezhang', 'longma', 'xinxu']
            }
        ]
    }

