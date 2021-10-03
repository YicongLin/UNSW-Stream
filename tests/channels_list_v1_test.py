from src.channels import channels_list_v1
import pytest
from src.error import AccessError
from src.other import clear_v1
def test_valid_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_list_v1('Invalid ID')
    
    

