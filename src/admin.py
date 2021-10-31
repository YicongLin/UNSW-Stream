from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from datetime import datetime, timezone
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.channel import check_valid_uid
from src.users import token_check
from src.channel import check_valid_uid

# ================================================
# ================== HELPERS =====================
# ================================================

# Raises an error if u_id belongs to a user who is the only global owner and is being removed
def remove_only_global_owner(u_id):
    # obtaining data
    data = data_store.get()
    emailpw = data['emailpw']

    # loop through data store to determine the number of total global owners,
    # as well as determining whether u_id belongs to a user who is a global owner
    permission_id_count = 0
    is_global_owner = False
    for i in range(len(emailpw)):
        if emailpw[i]['permissions_id'] == 1:
            permission_id_count += 1
        if emailpw[i]['u_id'] == u_id:
            if emailpw[i]['permissions_id'] == 1:
                is_global_owner = True 

    # raising the error
    if permission_id_count == 1 and is_global_owner == True:
        raise InputError(description="Cannot remove the only global owner")

# Raises an error if u_id belongs to a user who is the only global owner and is being demoted
def demote_only_global_owner(u_id):
    # obtaining data
    data = data_store.get()
    emailpw = data['emailpw']

    # loop through data store to determine the number of total global owners,
    # as well as determining whether u_id belongs to a user who is a global owner
    permission_id_count = 0
    is_global_owner = False
    for i in range(len(emailpw)):
        if emailpw[i]['permissions_id'] == 1:
            permission_id_count += 1
        if emailpw[i]['u_id'] == u_id:
            if emailpw[i]['permissions_id'] == 1:
                is_global_owner = True 
    
    # raising the error
    if permission_id_count == 1 and is_global_owner == True:
        raise InputError(description="Cannot demote the only global owner")

# Raises an error if the authorised user is not a global owner
def not_a_global_owner(token):
    # obtaining data
    data = data_store.get()
    emailpw = data['emailpw']
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # raising the error 
    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == auth_user_id:
            if emailpw[i]['permissions_id'] != 1:
                raise AccessError(description="You are not a global owner")

# ================================================
# ================= FUNCTIONS ====================
# ================================================

def admin_user_remove_v1(token, u_id):
    """Given a user by their u_id, remove the user from Streams.
   
    Arguments:
        token (string) - the token of a authorised user
        u_id (integer) - the ID of an existing and valid user
       
    Exceptions:
        InputError - Occurs when u_id does not refer to a valid and existing user
        InputError - Occurs when u_id refers to the only global user
        AccessError - Occurs when the authorised user is not a global owner
    
    Return Value:
        Empty dictionary on all valid conditions
    """
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    users = data['users']
    channel_details = data['channels_details']

    # checks for exceptions
    check_valid_uid(u_id) 
    token_check(token)
    remove_only_global_owner(u_id)
    not_a_global_owner(token)

    # otherwise, remove the user from Streams
    
    # removing the user from DM/s
    for i in range(len(dm_details)):
        dm_members = dm_details[i]['members']
        dm_creator = dm_details[i]['creator']
        dm_name = dm_details[i]['name']
        # removal from members list
        for j in range(len(dm_members)):
            if dm_members[j]['u_id'] == int(u_id):
                handle_str = dm_members[j]['handle_str']
                dm_members.remove(dm_members[j])
                data_store.set(data)
                break
        # removal from creator list
        if dm_creator[0]['u_id'] == int(u_id):
            dm_creator == []
            data_store.set(data)
        # removal from name list
        for j in range(len(dm_name)):
            if dm_name[j] == handle_str:
                dm_name.remove(dm_name[j])
                data_store.set(data)
                break
        
    # removing the user's message/s from DM/s
    for i in range(len(dm_details)):
        dm_messages = dm_details[i]['messages']
        for j in range(len(dm_messages)): 
            if dm_messages[j]['u_id'] == int(u_id):
                dm_messages[j]['message'] = 'Removed user'
                data_store.set(data)
    
    # removing the user from channel/s
    for i in range(len(channel_details)):
        channel_members = channel_details[i]['channel_members']
        channel_owner_members = channel_details[i]['owner_members']
        # removal from channel members list
        for j in range(len(channel_members)):
            if channel_members[j]['u_id'] == u_id:
                channel_members.remove(channel_members[j])
                data_store.set(data)
                break
        # removal from owner members list
        for j in range(len(channel_owner_members)):
            if channel_owner_members[j]['u_id'] == u_id:
                channel_owner_members.remove(channel_owner_members[j])
                data_store.set(data)
                break
    
    # removing the user's message/s from channel/s
    for i in range(len(channel_details)):
        channel_messages = channel_details[i]['messages']
        for j in range(len(channel_messages)): 
            if int(channel_messages[j]['u_id']) == int(u_id):
                channel_messages[j]['message'] = 'Removed user'
                data_store.set(data)
    
    # removing the user information from the list of users in the store
    # and placing them in a new store for deleted users
    for i in range(len(users)):
        if users[i]['u_id'] == u_id:
            deleted_user_dict = {
                'u_id': u_id,
                'email': '',
                'name_first': 'Removed',
                'name_last': 'user',
                'handle_str': ''
            }
            data['deleted_users'].append(deleted_user_dict)
            users.remove(users[i])
            break
    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    """Given a user by their u_id, set the user's permissions to new permissions described by permission_id.
   
    Arguments:
        token (string) - the token of a authorised user
        u_id (integer) - the ID of an existing and valid user
        permission_id (integer) - the ID of a user's permissions
       
    Exceptions:
        InputError - Occurs when u_id does not refer to a valid and existing user
        InputError - Occurs when u_id refers to the only global user and they are being demoted
        InputError - Occurs when permission_id is invalid
        AccessError - Occurs when the authorised user is not a global owner
    
    Return Value:
        Empty dictionary on all valid conditions
    """
    # obtaining data
    data = data_store.get()
    emailpw = data['emailpw']

    # checks for exceptions
    token_check(token)
    check_valid_uid(u_id)
    if permission_id == 2:
        demote_only_global_owner(u_id)
    if permission_id not in [1,2]:
        raise InputError(description="Invalid permission ID")
    not_a_global_owner(token)
    
    # otherise, change the user's permissions
    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == u_id:
            emailpw[i]['permissions_id'] = permission_id
    return {} 
