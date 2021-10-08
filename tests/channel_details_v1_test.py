import pytest
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1
 
# user with valid_id_1 creates the channel
# user with valid_id_2 joins the channel
# user with valid_id_2 invite user with valid_id_3
# user with valid_id_4 is not a memeber of channel (for comparison)

# No channels created
@pytest.fixture
def create_users():
    clear_v1()
    valid_id_1 = auth_register_v1("testperson@email.com", "password", "Test", "Person")['auth_user_id']
    valid_id_2 = auth_register_v1("testpersontwo@email.com", "passwordtwo", "Testtwo", "Persontwo")['auth_user_id']
    valid_id_3 = auth_register_v1("testpersonthr@email.com", "passwordthr", "Testthr", "Personthr")['auth_user_id']
    valid_id_4 = auth_register_v1("testpersonfour@email.com", "passwordfour", "Testfour", "Personfour")['auth_user_id']
    valid_id = [valid_id_1, valid_id_2, valid_id_3, valid_id_4] # store valid user id for return multiple valid id
    return valid_id
 
# Test raise AccessError
# auth_user_id not exists, but channel_id exists
def test_raise_AccessErrors_invlide_auth_user_id(create_users):
    valid_id = create_users
    valid_channel_id = channels_create_v1(valid_id[0], 'cse', True)
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,valid_channel_id)
    clear_v1()
    

# auth_user_id not exists
# auth_user_id exists but not a member of channel
def test_raise_AccessErrors_not_member(create_users):
    valid_id = create_users[0]
    valid_id_1 = create_users[1]
    valid_channel_id = channels_create_v1(valid_id, 'cse', True)["channel_id"] 
    with pytest.raises(AccessError):
        channel_details_v1(valid_id_1, valid_channel_id)
    clear_v1()

# Test raise InputError
# Valid auth_user_id but channel_id not exist
def test_raise_InputError_not_existed_channle_id(create_users):
    valid_id = create_users[0]
    with pytest.raises(InputError):
        channel_details_v1(valid_id, 99999999999)
    clear_v1()
 
# auth_user_ids are valid and they are members of the channel
def test_same_returen(create_users):
    valid_channel_id = create_users
    valid_id_1 = create_users[0]
    valid_id_2 = create_users[1]
    valid_id_3 = create_users[2]
    valid_channel_id = channels_create_v1(valid_id_1, 'cse', True)["channel_id"] # create a channel
    channel_join_v1(valid_id_2, valid_channel_id)
    channel_invite_v1(valid_id_2, valid_channel_id, valid_id_3)
    assert(channel_details_v1(valid_id_1, valid_channel_id) == channel_details_v1(valid_id_2, valid_channel_id) == channel_details_v1(valid_id_3, valid_channel_id))
    clear_v1()
 
# Test raise two errors and throw AccessError
def test_raise_two_errors_empty():
    with pytest.raises(AccessError):
        channel_details_v1('','')
    clear_v1() 

def test_raise_two_errors_strings():
    with pytest.raises(AccessError):
        channel_details_v1('Fake_id','Fake_channel')
    clear_v1() 

def test_raise_two_errors_spaces():
    with pytest.raises(AccessError):
        channel_details_v1('     ','  ')
    clear_v1() 

def test_raise_two_errors_int():
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,99999999999)
    clear_v1() 

def test_raise_two_errors_mix():
    with pytest.raises(AccessError):
        channel_details_v1(10000000000,'Fake_channel')
        channel_details_v1(' ','Fake_channel')
        channel_details_v1('Fake_id','')
    clear_v1()