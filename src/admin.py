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

# HELPER FUNCTIONS
# ==================================

# Returns true if u_id is a user who is the only global owner
def remove_only_global_owner(token, u_id):
    data = data_store.get()
    emailpw = data['emailpw']
    decoded_token = decode_JWT(token)
    auth_id = decoded_token['u_id']
    permission_id_count = 0
    is_global_owner = False
    for i in range(len(emailpw)):
        if emailpw[i]['permissions_id'] == 1:
            permission_id_count += 1
        if emailpw[i]['u_id'] == u_id:
            if emailpw[i]['permissions_id'] == 1:
                is_global_owner = True 
    
    if permission_id_count == 1 and is_global_owner == True:
        raise InputError(description="Cannot remove the only global owner")

def demote_only_global_owner(token, u_id):
    data = data_store.get()
    emailpw = data['emailpw']
    decoded_token = decode_JWT(token)
    auth_id = decoded_token['u_id']
    permission_id_count = 0
    is_global_owner = False
    for i in range(len(emailpw)):
        if emailpw[i]['permissions_id'] == 1:
            permission_id_count += 1
        if emailpw[i]['u_id'] == u_id:
            if emailpw[i]['permissions_id'] == 1:
                is_global_owner = True 
    
    if permission_id_count == 1 and is_global_owner == True:
        raise InputError(description="Cannot demote the only global owner")

# Returns true if the authorised user is not a global owner
def not_a_global_owner(token):
    data = data_store.get()
    emailpw = data['emailpw']
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == auth_user_id:
            if emailpw[i]['permissions_id'] != 1:
                raise AccessError(description="You are not a global owner")

# ==================================
# FUNCTIONS

def admin_user_remove_v1(token, u_id):

    #Obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # Check for valid u_id
    check_valid_uid(u_id) 
    
    # Check for invalid token
    token_check(token)

    # Raise an error if u_id refers to a user who is the only global owner
    remove_only_global_owner(token, u_id)
        
    # Raise an error if the authorised user is not a global owner
    not_a_global_owner(token)
    
    # Otherise, remove the user from the Streams

    # Removing user from DM/s
    dm_details = data['dms_details']
    for i in range(len(dm_details)):
        dm_members = dm_details[i]['members']
        for j in range(len(dm_members)):
            if dm_members[j]['u_id'] == u_id:
                dm_members.remove(dm_members[j])
    
    # Removing the user's message/s from DM/s
    for i in range(len(dm_details)):
        dm_messages = dm_details[i]['messages']
        for j in range(len(dm_messages)): 
            if dm_messages[j]['u_id'] == u_id:
                dm_messages[j]['message'] == 'Removed user'
    
    # Removing user from channel/s
    channel_details = data['channels_details']
    for i in range(len(channel_details)):
        channel_members = channel_details[i]['channel_members']
        channel_owner_members = channel_details[i]['owner_members']
        for j in range(len(channel_members)):
            if channel_members[j]['u_id'] == u_id:
                channel_members.remove(channel_members[j])
                break
        for j in range(len(channel_owner_members)):
            if channel_owner_members[j]['u_id'] == u_id:
                channel_owner_members.remove(channel_owner_members[j])
                break
    
    # Removing the user's message/s from channel/s
    for i in range(len(channel_details)):
        channel_messages = channel_details[i]['messages']
        for j in range(len(channel_messages)): 
            if int(channel_messages[j]['u_id']) == int(u_id):
                channel_messages[j]['message'] = 'Removed user'
                data_store.set(data)

                # channel_messages[j]['message'] == 'Removed user'
                break
    
    # Removing the user information from the list of users in the store
    # and placing them in a new store for deleted users
    users = data['users']
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
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # Check for invalid token
    token_check(token)
    
    # Check for valid u_id
    check_valid_uid(u_id)
    
    # Raising an error if u_id is the only global owner and they are being demoted to a user
    if permission_id == 2:
        demote_only_global_owner(token, u_id)
    # if only_global_owner(token, u_id) == True and permission_id == 2:
    #     raise InputError("Cannot demote the only global owner")
    
    # Check for valid permission_id
    if permission_id not in [1,2]:
        raise InputError(description="Invalid permission ID")
    
    # Raising an error if the authorised user is not a global owner
    not_a_global_owner(token)
    
    # Otherise, change the user's permissions
    emailpw = data['emailpw']
    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == u_id:
            emailpw[i]['permissions_id'] = permission_id
    return {} 
