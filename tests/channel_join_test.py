import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v1

# Creating valid channel and user IDs, 
# with one public channel and one private channel
@pytest.fixture
def valid_2_users():
    clear_v1()
    token_1 = auth_register_v2("abc@abc.com", "password", "abc", "def")['token']
    token_1 = auth_register_v2("zyx@wvu.com", "password", "zyx", "wvu")['token']
    channel_id_1 = channels_create_v2(id_1, "abc", True)['channel_id']
    channel_id_2 = channels_create_v2(id_2, "zyx", False)['channel_id']
    return token_1, token_1, channel_id_1, channel_id_2
    
# Testing for invalid channel ID
def test_invalid_channel(valid_2_users):
    token_1, *_ = valid_2_users
    with pytest.raises(InputError):
        channel_join_v2(token_1, "invalid_channel")
        
# Testing for a case where the user is already a member
def test_already_a_member(valid_2_users):
    token_1, _, channel_id_1, _ = valid_2_users
    with pytest.raises(InputError):
        channel_join_v2(token_1, channel_id_1)
        
# Testing for valid channel ID, and user is not already a member
def test_valid(valid_2_users):
    _, token_2, channel_id_1, _ = valid_2_users
    channel_join_v2(token_2, channel_id_1)

# Testing for users attempting to join private channels
def test_private_channel(valid_2_users):
    token_1, _, _, channel_id_2 = valid_2_users
    with pytest.raises(AccessError):
        channel_join_v2(token_1, channel_id_2)

# Testing for users attempting to join public channels
def test_public_channel(valid_2_users):
    _, token_2, channel_id_1, _ = valid_2_users  
    channel_join_v2(token_2, channel_id_1)


# Testing cases for wrong input
def test_empty():
    with pytest.raises(InputError):
        channel_join_v2("", "")

def test_symbols():
    with pytest.raises(InputError):
        channel_join_v2("#&$_*%", "#$(%}(")

def test_invalid_strings():
    with pytest.raises(InputError):
        channel_join_v2("invalid_id", "invalid_channel")

def test_combination():
    with pytest.raises(InputError):
        channel_join_v2("", "invalid_channel")
        channel_join_v2("invalid_id", "")
        channel_join_v2("", "#$(%}(")
        channel_join_v2("#&$_*%", "")
        channel_join_v2("#&$_*%", "invalid_channel")
        channel_join_v2("invalid_id", "#$(%}(") 


