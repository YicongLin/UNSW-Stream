import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v1

# Creating valid channel and user IDs, 
# with one public channel and one private channel
@pytest.fixture
def valid_3_users():
    clear_v1()
    token_1 = auth_register_v2("abc@abc.com", "password", "abc", "def")['token']
    token_2 = auth_register_v2("zyx@wvu.com", "password", "zyx", "wvu")['token']
    token_3 = auth_register_v2("mno@jkl.com", "password", "mno", "jkl")['token']
    channel_id_1 = channels_create_v2(id_1, "abc", True)['channel_id']
    channel_id_2 = channels_create_v2(id_2, "zyx", True)['channel_id']
    return token_1, token_2, token_3, channel_id_1, channel_id_2
    
# Testing for invalid channel ID
def test_invalid_channel(valid_3_users):
    token_1, token_2, *_ = valid_3_users
    with pytest.raises(InputError):
        channel_invite_v2(token_1, "invalid_channel", token_2)
        
# Testing for invalid u_id
def test_invalid_user(valid_3_users):
    token_1, _, _, channel_id_1, _ = valid_3_users
    with pytest.raises(AccessError):
        channel_invite_v2(token_1, channel_id_1, "invalid_id")
        
# Testing for valid channel ID and u_id
def test_valid(valid_3_users):
    token_1, token_2, _, channel_id_1, _ = valid_3_users
    channel_invite_v2(token_1, channel_id_1, token_2)

# Testing for a case where u_id refers to a user 
# who is already a member of the channel
def test_already_a_member(valid_3_users):
    token_1, token_2, _, channel_id_1, _ = valid_3_users
    channel_join_v2(token_1, channel_id_1)
    with pytest.raises(InputError):
        channel_invite_v2(token_1, channel_id_1, token_2)

# Testing for a case where u_id refers to a user 
# who is not already a member of the channel
def test_not_already_a_member(valid_3_users):
    token_1, token_2, _, channel_id_1, _ = valid_3_users
    channel_invite_v2(token_1, channel_id_1, token_2)
        
# Testing for a case where the authorised user 
# is not a member of the valid channel
def test_not_a_member(valid_3_users):
    token_1, _, token_3, _, channel_id_2 = valid_3_users
    with pytest.raises(AccessError):
        channel_invite_v2(token_1, channel_id_2, token_3)

# Testing for a case where the authorised user 
# is a member of the valid channel

def test_member(valid_3_users):
    token_1, _, token_3, channel_id_1, channel_id_2 = valid_3_users
    channel_invite_v2(token_1, channel_id_1, token_3)


# Testing cases for other invalid input
def test_empty():
    with pytest.raises(InputError):
        channel_invite_v2("", "", "")

def test_invalid_strings():
    with pytest.raises(InputError):
        channel_invite_v2("invalid_id_1", "invalid_channel", "invalid_id_2")

def test_symbols():
    with pytest.raises(InputError):
        channel_invite_v2("#&$_*%", "#$(%}(", "!@#$%^")

def test_combination():
    with pytest.raises(InputError):
        channel_invite_v2("", "", "invalid_id_1")
        channel_invite_v2("", "#$(%}(", "")
        channel_invite_v2("invalid_id_1", "", "!@#$%^")
        channel_invite_v2("invalid_id_1", "invalid_channel", "!@#$%^")
        channel_invite_v2("#&$_*%", "", "!@#$%^")
        channel_invite_v2("!@#$%^", "invalid_channel", "invalid_id_1")

