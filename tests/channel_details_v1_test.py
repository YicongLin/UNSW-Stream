import pytest

from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1

'''
# user with valid_id_1 creates the channel
# user with valid_id_2 joins the channel
# user with valid_id_2 invite user with valid_id_3
# user with valid_id_4 is not a memeber of channel (for comparison)
@pytest.fixture
def create_users_to_channel():
    clear_v1()
    valid_id_1 = auth_register_v1('cse@unsw.com', 'password', 'cse', 'lastnamecse')
    valid_id_2 = auth_register_v1('comp222@unsw.com', 'password', 'comp222', 'lastnamecomp222')
    valid_id_3 = auth_register_v1('comp333@unsw.com', 'password,' 'comp333', 'lastnamecomp333')
    valid_id_4 = auth_register_v1('comp444@unsw.com', 'password', 'comp444', 'lastnamecomp444')
    valid_channel_id = channels_create_v1(valid_id_1, 'cse', True)
    channel_join_v1(valid_id_2, valid_channel_id)
    channel_invite_v1(valid_id_2, valid_channel_id, valid_id_3)

# Test raise AccessError
# auth_user_id not exists
# auth_user_id exists but not a member of channel
def test_raise_AccessErrors_invlide_auth_user_id(create_users_to_channel):
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,valid_channel_id)

def test_raise_AccessErrors_not_member(create_users_to_channel):
    with pytest.raises(AccessError):
        channel_details_v1(valid_id_4, valid_channel_id)

# Test raise InputError
# Valid auth_user_id but channel_id not exist
def test_raise_InputError_not_existed_channle_id(create_users_to_channel):
    with pytest.raise(InputError):
        channel_details_v1(valid_id_1, 99999999999)

# auth_user_ids are valid and they are members of the channel
def test_same_returen(create_users_to_channel):
    assert(channel_details_v1(valid_id_1, valid_channel_id) == channel_details_v1(valid_id_2, valid_channel_id) == channel_details_v1(valid_id_3, valid_channel_id))
'''

# Test raise two errors and throw AccessError
def test_raise_two_errors_empty():
    clear_v1()
    with pytest.raises(AccessError):
        channel_details_v1('','')

def test_raise_two_errors_strings():
    clear_v1()
    with pytest.raises(AccessError):
        channel_details_v1('Fake_id','Fake_channel')

def test_raise_two_errors_int():
    clear_v1()
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,99999999999)

def test_raise_two_errors_mix():
    clear_v1()
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,'Fake_channel')
        channel_details_v1('','Fake_channel')
        channel_details_v1('Fake_id','')
