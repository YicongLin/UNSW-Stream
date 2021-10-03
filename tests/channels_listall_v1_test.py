import pytest

from src.channels import channels_listall_v1
from src.auth import auth_register_v1
from src.error import InputError
from src.other import clear_v1

# To continue test channels_listall_v1, auth_register_v1 is demanded
'''
@pytest.fixture
def create_auth_user_id():
    clear_v1()
    valid_id_1 = auth_register_v1(cse@unsw.com, password, cse, lastnamecse)
    valid_id_2 = auth_register_v1(comp@unsw.com, password, comp, lastnamecomp)
'''

def test_valid_id():
    clear_v1()
    with pytest.raises(InputError):
        channels_listall_v1('fake_id')

'''
def test_return_content(create_auth_user_id):
    assert channels_listall_v1(valid_id_1) == channels_listall_v1(valid_id_2)
'''

