import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v2, channel_leave_v1
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v2

# Creating valid channel and user IDs, 
# with one public channel and one private channel
@pytest.fixture
def valid_3_users():
    clear_v2()
    token_1 = auth_register_v1("abc@abc.com", "password", "abc", "def")["token"]
    token_2 = auth_register_v1("zyx@wvu.com", "password", "zyx", "wvu")["token"]
    token_3 = auth_register_v1("jkl@wvu.com", "password", "jkl", "mno")["token"]
    channel_id_1 = channels_create_v2(token_1, "abc", True)['channel_id']
    channel_join_v2(token_2, channel_id_1)
    return token_1, token_2, token_3, channel_id_1
    
# Testing for invalid channel ID
def test_invalid_channel(valid_3_users):
    token_1, *_ = valid_3_users
    with pytest.raises(InputError):
        channel_leave_v1(token_2, "invalid_channel")

# Testing for valid channel ID
def test_valid_channel(valid_3_users):
    token_1, _, _, channel_id_1 = valid_3_users
    channel_leave_v1(token_2, channel_id_1)


# Testing for a case where the user is not a member of the valid channel
def test_not_a_member(valid_3_users):
    _, _, token_3, channel_id_1 = valid_3_users
    with pytest.raises(AccessError):
        channel_leave_v1(token_3, channel_id_1)

# Testing for a case where the user is a member of the valid channel
def test_member(valid_3_users):
    token_1, _, _, channel_id_1 = valid_3_users
    channel_leave_v1(token_1, channel_id_1)

# Testing cases for wrong input
def test_empty():
    with pytest.raises(InputError):
        channel_leave_v1("", "")

def test_symbols():
    with pytest.raises(InputError):
        channel_leave_v1("", "#$(%}(")

def test_integer_token():
    with pytest.raises(InputError):
        channel_leave_v1(1, "invalid_channel")

def test_combination():
    with pytest.raises(InputError):
        channel_join_v1("", "invalid_channel")
        channel_join_v1(1, "")
        channel_join_v1(2, "#$(%}(")







