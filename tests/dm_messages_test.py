import pytest
from src.error import InputError, AccessError
from src.dm import dm_create_v1, dm_details_v1, dm_messages_v1
#from src.channel import channel_join_v1, channel_messages_v1, \
                        #channel_details_v1, channel_invite_v1
#from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1

# Creating a valid dm and user IDS
@pytest.fixture
def valid():
    clear_v1()
    id_1 = auth_register_v1("qwe@rty.com", "password", "uio", "qwe")['auth_user_id']
    id_2 = auth_register_v1("asd@fgh.com", "password", "jkl", "asd")['auth_user_id']
    dm_id_1 = dm_create_v1(id_1, "qwe", True)['dm_id']
    dm_id_2 = dm_create_v1(id_2, "asd", False)['dm_id']
    start_0 = 0
    return id_1, id_2, dm_id_1, dm_id_2, start_0

# Testing for an invalid dm
def test_invalid_dm(valid):
    id_1, _, _, _, start_0 = valid
    with pytest.raises(InputError):
        dm_messages_v1(id_1, "invalid_dm", start_0)
        
# Testing for a valid dm
def test_valid_dm(valid):
    id_1, _, dm_id_1, _, start_0 = valid
    dm_messages_v1(id_1, dm_id_1, start_0)
    
# Testing for when start is greater than the 
# total number of messages in the dm
def test_start_greater(valid):
    id_1, _, dm_id_1, _, start_0 = valid
    with pytest.raises(InputError):
        dm_messages_v1(id_1, dm_id_1, 2)

# # Testing for when start is less than or equal to the 
# # total number of messages in the dm
# def test_start_less_than(valid):
#     id_1, _, dm_id_1, _, start_5, start_10 = valid
#     messages = range(0, 10)
#     len(messages) == 10
#     dm_messages_v1(id_1, dm_id_1, start_10)
#     dm_messages_v1(id_1, dm_id_1, start_5)

# Testing for a case where the authorised user 
# is not a member of the valid dm
def test_not_a_member(valid):
    id_1, _, _, dm_id_2, start_0 = valid
    with pytest.raises(AccessError):
        dm_messages_v1(id_1, dm_id_2, start_0)

# Testing for a case where the authorised member 
# is a member of the valid dm
def test_dm_member(valid):
    id_1, _, dm_id_1, _, start_0 = valid
    dm_messages_v1(id_1, dm_id_1, start_0)

# Testing cases for other invalid input
def test_empty():
    with pytest.raises(InputError):
        dm_messages_v1("", "", 0)

def test_invalid_strings():
    with pytest.raises(InputError):         
        dm_messages_v1("invalid_id_1", "dm", 1)

def test_symbols():
    with pytest.raises(InputError):
        dm_messages_v1("#&$_*%", "#$(%}(", 1)

def test_combination():
    with pytest.raises(InputError):
        dm_messages_v1("", "", 1)
        dm_messages_v1("", "#$(%}(", 1)
        dm_messages_v1("invalid_id_1", "", 1)
        dm_messages_v1("invalid_id_1", "invalid_dm", 1)
        dm_messages_v1("#&$_*%", "", 1)
        dm_messages_v1("!@#$%^", "invalid_dm", 1)


 


