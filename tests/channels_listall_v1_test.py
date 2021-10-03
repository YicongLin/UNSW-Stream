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
    clear_v1()

@pytest.fixture
def channel_create(create_user):
    valid_id = create_user
    valid_id_1 = valid_id[0]
    valid_id_2 = valid_id[1]
    valid_id_3 = valid_id[2]
    channel_id1 = channels_create_v1(valid_id_1, 'Channel_one', True) # User with valid_id_1 create a Public channel called 'Channel_one'
    channel_idt2 = channels_create_v1(valid_id_1, 'Channel_two', False) # User with valid_id_1 create a Private channel called 'Channel_two'
    channel_idt3 = channels_create_v1(valid_id_2, 'Channel_three', False) # User with valid_id_2 create a Private channel called 'Channel_three'
    channel_idt4 = channels_create_v1(valid_id_3, 'Channel_four', True) # User with valid_id_3 create a Public channel called 'Channel_four'
    channels_id = [channel_id, channel_id, channel_id, cchannel_id]
    channel_num = 4
    return valid_id_1, valid_id_2, valid_id_3, channels_id

# No id have stored yet
# Without channels
def test_valid_id_1():
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


# # Return all channels (include pulic & private)
# def test_return_all_channels(channel_create):
#     all_data = channel_create
#     channels_id = channel_create[0]
#     valid_id = channel_create[1]
#     assert len(channels_listall_v1(valid_id_1)) == len(channels_listall_v1(valid_id_2)) == len(channels_listall_v1(valid_id_3)) == len(channels_id) == channel_num = 4

