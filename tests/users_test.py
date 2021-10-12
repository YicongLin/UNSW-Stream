import pytest
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.users import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1

@pytest.fixture
def valid():
    clear_v1()
    id_1 = auth_register_v1("u1@test.com", "password", "1first", "1last")['auth_user_id']
    id_2 = auth_register_v1("u2@test.com", "password", "2first", "2last")['auth_user_id']
    id_3 = auth_register_v1("u3@test.com", "password", "3first", "3last")['auth_user_id']
    return id_1, id_2, id_3

# USERS_ALL_V1
# correct list of all users + details 
def test_correct_list_all(valid):
    id_1, id_2, id_3 = valid
    users_all_v1(valid)

def test_correct_some(valid):
    id_1, _, id_3 = valid      
    users_all_v1(id_1, id_3)

# return empty list if no users 
def test_empty_list_all(valid):
    _, _, _ = valid
    assert users_all_v1(valid) == []

# USER_PROFILE_V1
# input error if invalid user 
def test_invalid_user():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_v1("token", 0)

# valid user
def test_valid_user():
    clear_v1()
    id_1 = auth_register_v1("u1@test.com", "password", "1first", "1last")['auth_user_id']
    user_profile_v1("token", id_1)

# valid users
def test_valid_users(valid):
    id_1, id_2, id_3 = valid
    user_profile_v1("token", id_1)
    user_profile_v1("token", id_2)
    user_profile_v1("token", id_3)

# USER_PROFILE_SETNAME_V1
# input error if length of name_first is not between 1 and 50 characters inclusive
def test_invalid_name_first():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_setname_v1("token", "", "lastname")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_setname_v1("token", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", "lastname")

# input error if length of name_last is not between 1 and 50 characters inclusive
def test_invalid_name_last():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_setname_v1("token", "firstname", "")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_setname_v1("token", "firstname", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm")

# valid first and last names 
def test_valid_names():
    clear_v1()
    user_profile_setname_v1("token", "firstname", "lastname")
    user_profile_setname_v1("token", "!@#$%^&**() ", "12345 67890")

# USER_PROFILE_SETEMAIL_V1
# input error if invalid email 
def test_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_setemail_v1("token", "invalidemail")

# input error if duplicate email 
def test_duplicate_email(valid):
    id_1, id_2, id_3 = valid
    with pytest.raises(InputError):
        user_profile_setemail_v1("token", "u1@test.com")

# valid emails
def test_valid_emails(valid):
    id_1, id_2, id_3 = valid
    user_profile_setemail_v1("token", "u1updated@test.com")
    user_profile_setemail_v1("token", "u3updated@test.com")

#USER_PROFILE_SETHANDLE_V1
# input error if length of handle_str is not between 3 and 20 characters inclusive
def test_invalid_handle():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "qwertyuiopasdfghjklzx")
        clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "as")

# input error if handle_str contains characters that are not alphanumeric
def test_nonalphanumeric_handle():
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "!@#$%^&*()")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "! ^&*()")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "! ")
    clear_v1()
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "1234567!@#$%")

# input error if duplicate handle 
def test_duplicate_handle(valid):
    id_1, id_2, id_3 = valid
    with pytest.raises(InputError):
        user_profile_sethandle_v1("token", "1first1last")

# valid handle 
def test_valid_handle(valid):
    user_profile_sethandle_v1("token", "validhandle")
    user_profile_sethandle_v1("token", "valid123handle")
    user_profile_sethandle_v1("token", "a2c")
    user_profile_sethandle_v1("token", "1234567890qwertyuiop")


