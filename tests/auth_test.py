import pytest
from src.auth import auth_login_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError

# REGISTER TESTS
# invalid email 
def test_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson", "password", "Test", "Person")

# duplicate email 
def test_register_duplicate_email():
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "Test", "Person")
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "Test", "Person")

# invalid password - less than 6 characters
def test_register_invalid_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "test", "Test", "Person")

# invalid first name - length of name_first is not between 1 and 50 characters inclusive
def test_register_invalid_firstname():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", 
            "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", "Person")
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "", "Person")

# invalid last name - length of name_last is not between 1 and 50 characters inclusive
def test_register_invalid_lastname():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "Test", 
            "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm")
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "Test", "")
        
# invalid first and last name 
def test_register_invalid_fullname():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm", 
            "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm")
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("testperson@email.com", "password", "", "")

# valid name
def test_valid():
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "  ", "   ")
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "Hello", "Hi")
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "@#$%", "%^&*")
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "@ a$%", "% a16&*")
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "1234", "5678")


   

# LOGIN TESTS 

# correct password 
def test_login_correct_pw():
    clear_v1()
    assert auth_register_v1("testperson@email.com", "password", "Test", "Person") == auth_login_v1("testperson@email.com", "password")
   
# incorrect password
def test_wrong_password(): 
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "Test", "Person")
    with pytest.raises(InputError):
        auth_login_v1("testperson@email.com", "wrongpassword")

# unregistered email 
def test_unregistered_email():
    clear_v1()
    auth_register_v1("testperson@email.com", "password", "Test", "Person")
    with pytest.raises(InputError):
        auth_login_v1("testperson1@email.com", "password")

# invalid email
def test_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("abc", "password", "Test", "Person")


    

    
