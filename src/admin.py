from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from datetime import datetime
import jwt
from src.token_helpers import decode_JWT

# HELPER FUNCTIONS
# ==================================

# Returns false if u_id does not refer to a valid user
def valid_uid(u_id):
    data = data_store.get()
    users = data['users']
    users_list = []
    for i in range(len(users)):
        users_list.append(users[i]['u_id'])
    if u_id not in users_list:
        return False

# Returns true if u_id is a user who is the only global owner
def only_global_owner(u_id)
    data = data_store.get()
    emailpw = data['emailpw']
    is_global_owner = False
    global_owner_list = []
    for i in range(len(emailpw)):
        if emailpw[i]['permissions_id'] == 1:
            global_owner_list.append(emailpw[i]['permissions_id'])
        if emailpw[i]['u_id'] == u_id:
            if emailpw[i]['permissions_id'] == 1:
                is_global_owner = True
    if is_global_owner == True:
        if len(global_owner_list) = 1:
            return True

# Returns true if the authorised user is not a global owner
def not_a_global_owner(token)
    data = data_store.get()
    emailpw = data['emailpw']
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == auth_user_id:
            if emailpw[i]['permissions_id'] != 1:
                return True

# Returns false if permission_id is invalid
def valid_permission_id(permission_id):
    if permission_id != 1 or permission_id != 2:
        return False

# ==================================
# FUNCTIONS

def admin_user_remove_v1(token, u_id):

    #Obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # Check for valid u_id
    valid_uid = valid_uid(u_id)
    if valid_uid == False:
        raise InputError("Invalid user")
    
    # Raise an error if u_id refers to a user who is the only global owner
    only_global_owner = only_global_owner(u_id)
    if only_global_owner == True:
        raise InputError("Cannot remove the only global owner")
        
    # Raise an error if the authorised user is not a global owner
    not_a_global_owner = not_a_global_owner(token)
    if not_a_global_owner == True:
        raise AccessError("You are not a global owner")
    
    # Otherise, remove the user from the Streams

    # Removing user from DM/s
    dm_details = data['dms_details']
    for i in range(len(dm_details)):
        dm_members = dm_details[i]['dm_members']
        for j in range(len(dm_members)):
            if dm_members[j]['u_id'] == u_id:
                remove(dm_members[j])
    
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
                remove(channel_members[j]
        for j in range(len(channel_owner_members)):
            if channel_owner_members[j]['u_id'] == u_id:
                remove(channel_owner_members[j])
    
    # Removing the user's message/s from channel/s
    for i in range(len(channel_details)):
        channel_messages = channel_details[i]['messages']
        for j in range(len(channel_messages)): 
            if channel_messages[j]['u_id'] == u_id:
                channel_messages[j]['message'] == 'Removed user'
    
    # Removing the user information from the list of users in the store
    # and placing them in a new store for deleted users
    users = data['users']
    for i in range(len(users)):
        if users[i]['u_id'] == u_id:
            deleted_user_dict = {
                'u_id': u_id
                'email': ''
                'name_first': 'Removed'
                'name_last': 'user'
                'handle_str': ''
            }
            data['deleted_users'].append(deleted_user_dict)
            remove(users[i])
    return {}

def admin_userpermission_changes_v1(token, u_id, permission_id):
    #Obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # Check for valid u_id
    valid_uid = valid_uid(u_id)
    if valid_uid == False:
        raise InputError("Invalid user")
    
    # Raising an error if u_id is the only global owner and they are being demoted to a user
    only_global_owner = only_global_owner(u_id)
    if only_global_owner == True and permission_id == 2:
        raise InputError("Cannot demote the only global owner")
    
    # Check for valid permission_id
    valid_permission_id = valid_permission_id(permission_id)
    if valid_permission_id == False:
        raise InputError("Invlid permission ID")
    
    # Raising an error if the authorised user is not a global owner
    not_a_global_owner = not_a_global_owner(token)
    if not_a_global_owner == True:
        raise AccessError("You are not a global owner")
    
    # Otherise, change the user's permissions
    emailpw = data['emailpw']
    for i in range(len(emailpw)):
        if emailpw[i]['u_id'] == u_id:
            emailpw[i]['permissions_id'] = permission_id
    return {} 
