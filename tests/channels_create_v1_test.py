import pytest
from src.error import InputError
from src.channels import channels_create_v1

def test_channel_create_fail():
    with pytest.raises(InputError):
        channels_create_v1(123456, '', False)
        channels_create_v1(123456, 'abfbabbcabdkbrafbakbfkab', False)
        channels_create_v1(1, '', True)
        channels_create_v1(2, 'dfdsjhkjhsdshkjfkjsdfjhjksdf  ', True)
