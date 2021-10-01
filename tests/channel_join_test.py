import pytest
from src.error import InputError, AccessError
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1


@pytest.fixture
def create_valid_channels():
    clear_v1()
    valid_id_1 = auth_register_v1("abc@abc.com", "password", "abc", "def"
    valid_id_2 = auth_register_v1("zyx@wvu.com", "password", "zyx", "wvu"
    valid_id_3 = auth_register_v1("mno@jkl.com", "password", "mno", "jkl"
    valid_channel_id_1 = channels_create_v1(valid_id_1, "abc", TRUE) 
    valid_channel_id_2 = channels_create_v1(valid_id_2, "zyx", FALSE) 
    

def test_invalid_channel():
    with pytest.raises(InputError):
        channel_join_v1(valid_id_1, "00000")

def test_already_a_member():
    with pytest.raises(InputError):
        channel_join_v1(valid_id_1, valid_channel_id_1)
        channel_join_v1(valid_id_2, valid_channel_id_2)
        
def test_private_channel():
    with pytest.raises(AccessError):
        channel_join_v1(valid_id_1, valid_channel_2)
        channel_join_v1(valid_id_3, valid_channel_2)
        
    
    
