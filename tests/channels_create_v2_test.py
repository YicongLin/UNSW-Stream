""" import pytest
from src.channels import channels_create_v2
from src.auth import 
from src.error import InputError
def test_channel_create():
    

    with pytest.raises(InputError):
        channels_create_v2(id_1, '', False)
        channels_create_v2(id_1, 'abfbabbcabdkbrafbakbfkab', False)
        channels_create_v2(id_1, '', True)
        channels_create_v2(id_1, 'dfdsjhkjhsdshkjfkjsdfjhjksdf  ', True)
     """
    
    

 

