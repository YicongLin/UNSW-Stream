from src.channels import channels_list_v1
import pytest
from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1

@pytest.fixture
def valid():
    clear_v1()
    id_1 = auth_register_v1("abc@abc.com", "password", "abc", "def")['auth_user_id']
    id_2 = auth_register_v1("bde@bde.com", "asdfghj", "zyx", "wvu")['auth_user_id']
    channel_1 = channels_create_v1(id_1, "abc", True)
    channel_2 = channels_create_v1(id_2, "def", True)
    return id_1, id_2, channel_1, channel_2

# Testing for an invalid ID
def test_invalid_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_list_v1('Invalid ID')

# Testing for a valid ID
def test_valid_id(valid):
    id_1, *_ = valid 
    channels_list_v1(id_1)
    
# Ensuring that there are no duplicate channels
def test_no_duplicates(valid):
    _, _, channel_1, channel_2 = valid
    assert len(channel_1) == len(channel_2) == 1


    
    

