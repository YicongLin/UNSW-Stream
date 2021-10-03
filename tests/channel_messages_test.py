import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v1, channel_messages_v1, channel_details_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.data_store import data_store

# Creating a valid channel and user IDS
@pytest.fixture
def valid():
    clear_v1()
    id_1 = auth_register_v1("qwe@rty.com", "password", "uio", "qwe")
    id_2 = auth_register_v1("asd@fgh.com", "password", "jkl", "asd")
    channel_id_1 = channels_create_v1(id_1, "qwe", True)
    channel_id_2 = channels_create_v1(id_2, "asd", False)
    start_5 = 5
    start_10 = 10
    return id_1, id_2, id_3, channel_id_1, channel_id_2, start

# Testing for an invalid channel
def test_invalid_channel(valid):
    id_1, _, _, _, start = valid()
    with pytest.raises(InputError):
        channel_messages_v1(id_1, "invalid_channel", start)
        
# Testing for a valid channel
def test_valid_channel
    id_1, _, channel_id_1, _, start = valid()
    channel_messages_v1(id_1, channel_id_1, start)
    
# Testing for when start is greater than the 
# total number of messages in the channel
def test_valid_channel
    id_1, _, channel_id_1, _, start = valid()
    data = data_store.get()
    messages = data["channel_details"]["messages"]
    assert len(messages.columns) = 3
    with pytest.raises(InputError):
        channel_messages_v1(id_1, channel_id_1, start)

# Testing for when start is less than or equal to the 
# total number of messages in the channel
def test_valid_channel
    id_1, _, channel_id_1, _, start = valid()
    data = data_store.get()
    messages = data["channel_details"["messages"]
    assert len(messages.columns) = 10
    channel_messages_v1(id_1, channel_id_1, start_10)
    channel_messages_v1(id_1, channel_id_1, start_5)

# Testing for a case where the authorised user 
# is not a member of the valid channel
def test_not_a_member(valid):
    id_1, _, _, channel_id_2 = valid
    with pytest.raises(AccessError):
        channel_messages_v1(id_1, channel_id_2, start_10)

# Testing for a case where the authorised member 
# is a member of the valid channel
def test_channel_member(valid):
    id_1, _, channel_id_1, _ = valid
    channel_messages_v1(id_1, channel_id_1, start_10)

# Testing cases for other invalid input
def test_empty():
    with pytest.raises(InputError):
        channel_messages_v1("", "", "")

def test_invalid_strings():
    with pytest.raises(InputError):         
    channel_invite_v1("invalid_id_1", "invalid_channel", "invalid_start")

def test_symbols():
    with pytest.raises(InputError):
        channel_invite_v1("#&$_*%", "#$(%}(", "!@#$%^")

def test_combination():
    with pytest.raises(InputError):
        channel_invite_v1("", "", "invalid_start")
        channel_invite_v1("", "#$(%}(", "")
        channel_invite_v1("invalid_id_1", "", "!@#$%^")
        channel_invite_v1("invalid_id_1", "invalid_channel", "!@#$%^")
        channel_invite_v1("#&$_*%", "", "!@#$%^")
        channel_invite_v1("!@#$%^", "invalid_channel", "invalid_start")


 


