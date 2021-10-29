# import pytest
# from src.error import InputError
# from src.channels import channels_create_v1
# from src.other import clear_v1
# from src.auth import auth_register_v1

# # Creating valid channel and user IDs
# @pytest.fixture
# def valid():
#     clear_v1()
#     id_1 = auth_register_v1("abc@abc.com", "password", "abc", "def")['auth_user_id']
#     return id_1

# # Testing for an invalid name
# def test_invalid_name(valid):
#     id_1 = valid
#     with pytest.raises(InputError):
#         channels_create_v1(id_1, '', False)
#         channels_create_v1(id_1, 'abfbabbcabdkbrafbakbfkab', False)
#         channels_create_v1(id_1, '', True)
#         channels_create_v1(id_1, 'dfdsjhkjhsdshkjfkjsdfjhjksdf  ', True)
        
# # Testing for a valid name
# def test_valid_name(valid):
#     id_1 = valid
#     channels_create_v1(id_1, 'abc', False)
    
# # Testing for a name with just space
# def test_space(valid):
#     id_1 = valid
#     channels_create_v1(id_1, '  ', True)
    
#  # Testing for a name with numbers
# def test_numbers(valid):
#     id_1 = valid
#     channels_create_v1(id_1, '12345', False)

#  # Testing for a name with symbols
# def test_numbers(valid):
#     id_1 = valid
#     channels_create_v1(id_1, '@#^&$*', False)

# # Testing for a combination
# def test_combination(valid):
#     id_1 = valid
#     channels_create_v1(id_1, 'a 1bd$%', False)
#     channels_create_v1(id_1, 'jfd75&8*', False)
#     channels_create_v1(id_1, 'a b c $ 5 6 ^', False)
    
    
    

 

