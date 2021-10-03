import pytest
from src.channels import channels_listall_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def create_user():
    clear_v1()
    valid_id_1 = auth_register_v1("testperson@email.com", "password", "Test", "Person")
    valid_id_2 = auth_register_v1("testpersontwo@email.com", "passwordtwo", "Testtwo", "Persontwo")
    valid_id_3 = auth_register_v1("testpersonthr@email.com", "passwordthr", "Testthr", "Personthr")
    valid_id = [valid_id_1, valid_id_2, valid_id_3] # store valid user id for return multiple valid id
    return valid_id

# No id have stored yet
# Without channels
def test_valid_id_1():
    clear_v1()
    with pytest.raises(AccessError):
        channels_listall_v1('fake_id')
        channels_listall_v1(123123123123) # Impossible Id for now
        channels_listall_v1(         )
        channels_listall_v1(',.-;[]')
    clear_v1()

# Id have stored
# Without channels
def test_valid_id_2(create_user):
    valid_id = create_user
    with pytest.raises(AccessError):
        channels_listall_v1('fake_id')
        channels_listall_v1(123123123123) # Impossible Id for now
        channels_listall_v1(         )
        channels_listall_v1(',.-;[]')
    clear_v1()

# Id have stored
# With channels
def test_valid_id_3(create_user):
    valid_id = create_user
    with pytest.raises(AccessError):
        channels_listall_v1('fake_id')
        channels_listall_v1(123123123123) # Impossible Id for now
        channels_listall_v1(         )
        channels_listall_v1(',.-;[]')
    clear_v1()

# Three valid id show return same content
# Without channels
def test_return_content(create_user):
    valid_id = create_user
    assert channels_listall_v1(valid_id[0]) == channels_listall_v1(valid_id[1]) == channels_listall_v1(valid_id[2])
    clear_v1()


# def test_return_content_1(create_user):
#     valid_id = create_user
#     channel_id_1 = channels_create_v1(valid_id[0], "abc", True)
#     channel_id_2 = channels_create_v1(id_2, "zyx", False)
#     assert channels_listall_v1(valid_id[0]) == channels_listall_v1(valid_id[1]) == channels_listall_v1(valid_id[2])
#     clear_v1()









