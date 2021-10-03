import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1

# Creating a valid channel and user IDS
def valid():
    clear_v1()
    id_1 = auth_register_v1("qwe@rty.com", "password", "uio", "qwe")
    id_2 = auth_register_v1("asd@fgh.com", "password", "jkl", "asd")
    id_3 = auth_register_v1("asd@fgh.com", "password", "jkl", "asd")
    channel_id_1 = channels_create_v1(id_1, "qwe", True)
    channel_id_2 = channels_create_v1(id_2, "asd", False)
    return id_1, id_2, id_3, channel_id_1, channel_id_2

# Testing for an invalid channel
def test_invalid_channel_message
id_1, *_ = valid()
    with pytest.raises(InputError):
    channel_messages_v1(id_1, "00000")

# Testing for authorised member in a valid channel
def test_authorised_member_message
    with pytest.raises(AccessError):

# Testing if the start is greater than the total number of messages in the channel
def test_invalid_start
    with pytest.raises(InputError):

# Testing functionality
def test_channel_messages():
    clear()
    # Test that there are currently 0 messages in the channel
    assert channel_messages_v1(,0) == {'start': 0, 'end': -1, 'messages': []}
    assert channel_messages_v1
    


