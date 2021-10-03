# import pytest
# from src.error import InputError, AccessError
# from src.channel import channel_join_v1, channel_invite_v1
# from src.channels import channels_create_v1
# from src.auth import auth_register_v1
# from src.other import clear_v1

# # Creating valid channel and user IDs, 
# # with one public channel and one private channel
# @pytest.fixture
# def valid_3_users():
#     clear_v1()
#     id_1 = auth_register_v1("abc@abc.com", "password", "abc", "def")
#     id_2 = auth_register_v1("zyx@wvu.com", "password", "zyx", "wvu")
#     id_3 = auth_register_v1("mno@jkl.com", "password", "mno", "jkl")
#     channel_id_1 = channels_create_v1(id_1, "abc", True)
#     channel_id_2 = channels_create_v1(id_2, "zyx", True)
#     return id_1, id_2, id_3, channel_id_1, channel_id_2
    
# # Testing for invalid channel ID
# def test_invalid_channel(valid_3_users):
#     id_1, id_2, *_ = valid_3_users
#     with pytest.raises(InputError):
#         channel_invite_v1(id_1, "invalid_channel", id_2)
        
# # Testing for invalid u_id
# def test_invalid_user(valid_3_users):
#     id_1, _, _, channel_id_1, _ = valid_3_users
#     with pytest.raises(InputError):
#         channel_invite_v1(id_1, channel_id_1, "invalid_id")
        
# # Testing for valid channel ID and u_id
# def test_valid(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_2)

# # Testing for a case where u_id refers to a user 
# # who is already a member of the channel
# def test_already_a_member(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_join_v1(id_2, channel_id_1)
#     with pytest.raises(InputError):
#         channel_invite_v1(id_1, channel_id_1, id_2)

# # Testing for a case where u_id refers to a user 
# # who is not already a member of the channel
# def test_not_already_a_member(valid_3_users):
#     id_1, id_2, _, channel_id_1, _ = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_2)
        
# # Testing for a case where the authorised user 
# # is not a member of the valid channel
# def test_not_a_member(valid_3_users):
#     id_1, _, id_3, _, channel_id_2 = valid_3_users
#     with pytest.raises(AccessError):
#         channel_invite_v1(id_1, channel_id_2, id_3)

# # Testing for a case where the authorised user 
# # is a member of the valid channel

# def test_member(valid_3_users):
#     id_1, _, id_3, channel_id_1, channel_id_2 = valid_3_users
#     channel_invite_v1(id_1, channel_id_1, id_3)


# # Testing cases for other invalid input
# def test_empty():
#     with pytest.raises(InputError):
#         channel_invite_v1("", "", "")

# def test_invalid_strings():
#     with pytest.raises(InputError):
#         channel_invite_v1("invalid_id_1", "invalid_channel", "invalid_id_2")

# def test_symbols():
#     with pytest.raises(InputError):
#         channel_invite_v1("#&$_*%", "#$(%}(", "!@#$%^")

# def test_combination():
#     with pytest.raises(InputError):
#         channel_invite_v1("", "", "invalid_id_1")
#         channel_invite_v1("", "#$(%}(", "")
#         channel_invite_v1("invalid_id_1", "", "!@#$%^")
#         channel_invite_v1("invalid_id_1", "invalid_channel", "!@#$%^")
#         channel_invite_v1("#&$_*%", "", "!@#$%^")
#         channel_invite_v1("!@#$%^", "invalid_channel", "invalid_id_1")

