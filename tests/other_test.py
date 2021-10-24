import pytest
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.data_store import data_store

# Function to make users join
@pytest.fixture
def random_users_join():
    id_1 = auth_register_v1("qrt@xyz.com", "password", "qrt", "yuh")['auth_user_id']
    id_2 = auth_register_v1("oki@lam.com", "password", "oki", "buk")['auth_user_id']
    channel_id_1 = channels_create_v1(id_1, "qrt", True)["channel_id"]
    channel_id_2 = channels_create_v1(id_2, "buk", False)["channel_id"]
    return id_1, id_2, channel_id_1, channel_id_2
    
# Checking user is not in channel after clear function is called
def test_clear_joined_user(random_users_join):
    data = data_store.get()
    _, id_2, channel_id_1, _ = random_users_join
    channel_join_v1(id_2, channel_id_1)
    clear_v1()
    assert data['users'] == []
    
# Checking data store is cleared by the function
def test_clear_data():
    data = data_store.get()
    clear_v1()
    assert data['users'] == []
    assert data['channels'] == []
    assert data['channels_details'] == []
    assert data['emailpw'] == []
    assert data['dms_details'] == []
