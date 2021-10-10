import pytest
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.users import users_all_v1

@pytest.fixture
def valid():
    clear_v1()
    id_1 = auth_register_v1("u1@test.com", "password", "1first", "1last")['auth_user_id']
    id_2 = auth_register_v1("u2@test.com", "password", "2first", "2last")['auth_user_id']
    id_3 = auth_register_v1("u3@test.com", "password", "3first", "3last")['auth_user_id']
    return id_1, id_2, id_3

# USERS ALL 
# correct list of all users + details 
def test_correct_list_all(valid):
    id_1, id_2, id_3 = valid
    users_all_v1(valid)

# incorrect list 


# return empty list if no users 



# USERS PROFILE 
# invalid user - input error 


# correct list 


# incorrect list 


# return empty list if no users 

