import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1

# Creating valid channel and user IDs, 
# with one public channel and one private channel
def create_two_channels():
    clear_v1()
    valid_id_1 = auth_register_v1("abc@abc.com", "password", "abc", "def")
    valid_id_2 = auth_register_v1("zyx@wvu.com", "password", "zyx", "wvu")
    valid_id_3 = auth_register_v1("mno@jkl.com", "password", "mno", "jkl")
    valid_channel_id_1 = channels_create_v1(valid_id_1, "abc", True)
    valid_channel_id_2 = channels_create_v1(valid_id_2, "zyx", False)
    
# Testing for invalid channel ID
def test_invalid_channel():
    create_two_channels()
    with pytest.raises(InputError):
        channel_join_v1(valid_id_1, "invalid_channel")

# Testing for a case where the user is already a member
def test_already_a_member():
    create_two_channels()
    with pytest.raises(InputError):
        channel_join_v1(valid_id_1, valid_channel_id_1)
        channel_join_v1(valid_id_2, valid_channel_id_2)

# Testing for users attempting to join private channels
def test_private_channel():
    create_two_channels()
    with pytest.raises(AccessError):
        channel_join_v1(valid_id_1, valid_channel_2)
        channel_join_v1(valid_id_3, valid_channel_2)

# Testing cases for wrong input
def test_empty():
    create_two_channels()
    with pytest.raises(AccessError):
        channel_join_v1("", "")

def test_integers():
    create_two_channels()
    with pytest.raises(AccessError):
        channel_join_v1("12345", "678910")

def test_invalid_strings():
    create_two_channels()
    with pytest.raises(AccessError):
        channel_join_v1("invalid_id", "invalid_channel")

def test_combination():
    create_two_channels()
    with pytest.raises(AccessError):
        channel_join_v1("", "invalid_channel")
        channel_join_v1("invalid_id", "")
        channel_join_v1("", "12345")
        channel_join_v1("12345", "")
        channel_join_v1("12345", "invalid_channel")
        channel_join_v1("invalid_id", "12345") 

