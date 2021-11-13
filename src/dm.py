""" this file contains important functions: dm create, remove, list, detail and leave as well as same helpers """
from _pytest.python_api import raises
from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.channel import check_valid_token
from src.message import add_notification
from datetime import datetime, timezone
import math

secret = 'COMP1531'

# ============================================================
# ===========(Raise errors and associate functions)===========
# ============================================================

# ==================================
# Check dm_id valid or not
# Serach information at data['dms_details']
# If dm_id is invalid then return False
# If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
def check_valid_dmid(dm_id):
    """ Check dm_id valid or not """
    
    data = data_store.get()

    dm_id = int(dm_id)
    dms_element = 0
    all_dm_id = []
    while dms_element  < len(data['dms_details']):
        all_dm_id.append(data['dms_details'][dms_element]['dm_id'])
        dms_element += 1

    dm_id_element = 0
    while dm_id_element < len(all_dm_id):
        if dm_id == all_dm_id[dm_id_element]:
            break
        dm_id_element += 1
            
    if dm_id not in all_dm_id :
        raise InputError(description="Invalid dm_id")

    return dm_id_element 
# Finish valid dm_id check
# ==================================

# ==================================
# Check authorised user is an member of dm or not
# Serach information at data['dms_details'][dm_id_element]['dm_members']
# If authorised user is a not member of dm then return False
# If authorised user is a member of dm then return member_id_element (its index at dm_members[member_id_element])
def check_valid_dm_token(auth_user_id, dm_id_element):    
    data = data_store.get()

    members_in_dm = data['dms_details'][dm_id_element]['members']
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_dm):
        each_member_id.append(members_in_dm[each_member_element]['u_id'])
        each_member_element += 1

    if auth_user_id not in each_member_id:
        raise AccessError(description="Login user has not right to access dm_details")

    return each_member_id
# Finish  authorised user member check
# ==================================

# ==================================
# Find out the index of auth_user within dm['members']
# Return the index of auth_user within dm['members']
def auth_user_dm_index(each_member_id, auth_user_id):
    member_id_element = 0

    while True:
        if each_member_id[member_id_element] == auth_user_id:
            return member_id_element
        member_id_element += 1

# Finish index finding
# ==================================

# ==================================
# Check whether the start of messages is greater than 
# the total number of messages or not.
# Returns true if start is greater. 
def start_greater(dm_id, start):
    data = data_store.get()
    dms = data["dms_details"]
    
    for i in range(len(dms)):
        if int(dm_id) == dms[i]["dm_id"]:
            x = dms[i]
            messages = x["messages"]
            if int(start) > len(messages):
                raise InputError("Exceeded total number of messages in this dm") 
# Finish messages check
# ==================================

# ==================================
# Check whether the user of the given ID is a member of the DM or not;
# Returns false if the user is not a member
def check_dm_member(dm_id, u_id):
    data = data_store.get()
    dms = data["dms_details"]

    # Extracting the given DM's index
    dm_count = 0
    for i in range(len(dms)):
        if dms[i]["dm_id"] == int(dm_id):
            break
        dm_count += 1

    members = dms[dm_count]['members']
    member_list = []
    for i in range(len(members)):
        member_list.append(members[i]['u_id'])

    if u_id not in member_list:
        raise AccessError("You are not a member of the dm")  

# Finish DM member check
# ==================================

# ==================================
# Update 'dms_joined' when a user leave a dm
def dms_joined_num_leave(auth_user_id):
    data = data_store.get()

    # "normal" timestamp for changing number of dms that user is member to
    now_time = datetime.now().timestamp()

    # Pick out user's index in ['timestamps']['users']
    timestamps_user_index = 0
    while True:
        if data['timestamps']['users'][timestamps_user_index]['u_id'] == auth_user_id:
            break
        timestamps_user_index += 1

    # Obtain user's lately dm info
    lately_dms_joined_index = len(data['timestamps']['users'][timestamps_user_index]['dms_joined']) - 1
    lately_dms_joined_num = data['timestamps']['users'][timestamps_user_index]['dms_joined'][lately_dms_joined_index]['num_dms_joined']
    
    # Update dm user's dm info
    new_dms_joined = {
        "num_dms_joined" : (lately_dms_joined_num - 1), 
        "time_stamp" : int(now_time)
    }
    data['timestamps']['users'][timestamps_user_index]['dms_joined'].append(new_dms_joined)

    data_store.set(data)

    pass
# Finish function
# ==================================

# ==================================
# Update 'dms_joined' when a user join a dm
def dms_joined_num_join(auth_user_id):
    data = data_store.get()

    # "normal" timestamp for changing number of dms that user is member to
    now_time = datetime.now().timestamp()

    # Pick out user's index in ['timestamps']['users']
    timestamps_user_index = 0
    while True:
        if data['timestamps']['users'][timestamps_user_index]['u_id'] == auth_user_id:
            break
        timestamps_user_index += 1

    lately_dms_joined_index = len(data['timestamps']['users'][timestamps_user_index]['dms_joined']) - 1
    lately_dms_joined_num = data['timestamps']['users'][timestamps_user_index]['dms_joined'][lately_dms_joined_index]['num_dms_joined']
    
    # Update dm user's dm info
    new_dms_joined = {
        "num_dms_joined" : (lately_dms_joined_num + 1), 
        "time_stamp" : int(now_time)
    }
    data['timestamps']['users'][timestamps_user_index]['dms_joined'].append(new_dms_joined)

    pass
# Finish function
# ==================================

# ==================================
# Update workspace data store when a user creates a DM
def timestamps_update_create_dm():
    data = data_store.get()
    time_created = int(datetime.now().timestamp())
    workspace = data['timestamps']['workspace']

    num_dms = workspace['dms_exist'][-1]['num_dms_exist'] + 1
    dms_dict = {
        'num_dms_exist': num_dms,
        'time_stamp': time_created
    }
    workspace['dms_exist'].append(dms_dict)
    
    data_store.set(data)

# Finish timestamps data store update
# ==================================



# ============================================================
# =====================(Actual functions)=====================
# ============================================================


def dm_details_v1(token, dm_id):
    """An authorised user to check a dm’s detailed information which user is a member of it
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        dm_id (integer) - the ID of an existing dm

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user is not a member of that dm
        InputError - Occurs when authorised user type in an invalid dm id

    Return Value:
        {name, members}
            name (string) - name of dm
            members(a list of dict): [{u_id, email, name_first, name_last, handle_str}]
                u_id (integer) - the ID of an authorised user
                email (string) - the email of an authorised user
                first name (string) - first name of an authorised user
                last name (string) - last name of an authorised user
                handle_str (string) - special string created for authorised user
    """

    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid dm_id
    # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)

    auth_user_id = decode_JWT(token)['u_id']
    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    check_valid_dm_token(auth_user_id, dm_id_element)

    # Pick out dm name and its members from data['dms_details'][dm_id_element]
    name = data['dms_details'][dm_id_element]['name']
    members = data['dms_details'][dm_id_element]['members']

    return {
        'name': name,
        'members': members
    }


def dm_leave_v1(token, dm_id):
    """An authorised user leaves a dm
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        dm_id (integer) - the ID of an existing dm

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user is not a member of that dm
        InputError - Occurs when authorised user type in an invalid dm id

    Return Value:
        {}
    """

    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid dm_id
    # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)

    auth_user_id = decode_JWT(token)['u_id']

    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    # If authorised user is a member of dm then return member_id_element (its index at dm_members[member_id_element])
    each_member_id = check_valid_dm_token(auth_user_id, dm_id_element)
    member_id_element = auth_user_dm_index(each_member_id, auth_user_id)

    # Pick out dict from dm's members and then delete it 
    leave_dm_member = data['dms_details'][dm_id_element]['members'][member_id_element]
    data['dms_details'][dm_id_element]['members'].remove(leave_dm_member)

    dms_joined_num_leave(auth_user_id)

    data_store.set(data)

    return {}

def dm_create_v1(token, u_ids):
    """An authorised user creates a dm with a list of u_ids 

    Arguments:
        token (string) - a token contains u_id, session_id and permission_id
        u_ids (list) - a list of u_ids of valid users, exclude the creator

    Exceptions:
        AccessError - invalid token
        InputError - one of more u_ids are invalid

    Return Value:
        {
            dm_id(int)
        }
    """
    
    # check is the token passed in is valid, if not it will raise an access error
    is_valid_token(token)
    data = data_store.get()
    dm = data['dms_details']
    user_id = decode_token(token)

    # check if the u_ids passed in are all valid, if not it will raise an input error
    check_user(u_ids)
    
    creator_detail = get_member_detail([user_id])
    
    new_dm_id = len(dm) + 1
    u_ids.append(user_id)
    handle_str = get_name(u_ids)
    member_detail = get_member_detail(u_ids)

    dm_detail_dict = {
        'dm_id': new_dm_id,
        'name': handle_str,
        'members': member_detail,
        'creator': creator_detail,
        'messages': []
    }
    
    creator_handle = creator_detail[0]['handle_str']
    
    notification_dict = {
        'channel_id': -1,
        'dm_id': new_dm_id,
        'notification_message': creator_handle + " added you to " + handle_str
    }   
    i = 0
    while i < len(u_ids) - 1:
        add_notification(notification_dict, u_ids[i])
        i += 1

    data['dms_details'].append(dm_detail_dict)

    # Recursion to update timestamp
    uids_index = 0
    while uids_index < len(u_ids):
        dms_joined_num_join(u_ids[uids_index])
        uids_index += 1

    data_store.set(data)

    timestamps_update_create_dm()

    return {
        'dm_id': new_dm_id
    }

def decode_token(token):
    """ decode a token and get the u_id """
    secret = 'COMP1531'
    result = jwt.decode(token, secret, algorithms=['HS256'])['u_id']
    u_id = result
    return u_id


 
def check_user(u_ids):
    """ a function to check if the user in u_ids is a valid user """
    
    data = data_store.get()
    users_dict = data['users']
    user_id_list = []
    if (len(u_ids) >= 1):
        a = 0
        while a < len(users_dict):
            user_id_list.append(users_dict[a]['u_id'])
            a += 1
        b = 0
        while b < len(u_ids):
            if (u_ids[b] not in user_id_list):
                raise InputError(description="There is 1 or more invalid ids, please check again")
            b += 1
    
    return 
 

def get_member_detail(id_list):
    """ get the members details that on the list passed in """
    
    data = data_store.get()

    users_dict = data['users']
    user_detail_list = []
    i = 0
    while i < len(id_list):
        j = 0
        while j < len(users_dict):
            if (id_list[i] == users_dict[j]['u_id']):
                user_detail_list.append(users_dict[j])
            j += 1
        i += 1
    return user_detail_list


 
def get_name(id_list):
    """ get every users'handle_str and append them in a list """
    
    data = data_store.get()
    users_dict = data['users']
    names_list = []
    i = 0
    while i < len(id_list):
        j = 0
        while j < len(users_dict):
            if (id_list[i] == users_dict[j]['u_id']):
                names_list.append(users_dict[j]['handle_str'])
            j += 1
        i += 1
    names_list = sorted(names_list)
    return ', '.join(names_list)


def dm_remove_v1(token, dm_id):
    
    """An authorised user removes an existing dm, it can only be done by the owner of this dm

    Arguments:
        token (string) - a token contains u_id, session_id and permission_id
        dm_id (int) - the dm that will be removed

    Exceptions:
        AccessError - if the auth user is not the owner of the dm
        InputError - if the dm_id is invalid
        AcessError - if the auth user is not a valid user
    Return Value:
        {

        }
    """
    
    # check is the token passed in is valid, if not it will raise an access error
    is_valid_token(token)
    
    data = data_store.get()
    dm_detail_info = data['dms_details']
    user_id = decode_token(token)
    
    
    # checking for both errors
    i = 0
    input = 0
    access = 0
    while i < len(dm_detail_info):
        if (dm_detail_info[i]['dm_id'] == dm_id):
            input = 1
            creator = dm_detail_info[i]['creator']
            if (user_id == creator[0]['u_id']):
                access = 1
        i += 1
    # didn't find the dm id in datastore
    if (input == 0):
        raise InputError(description="Invalid DM ID")

    # the user passed in is not the creator of this dm
    if (access == 0):
        raise AccessError(description="Access denied, user is not a creator of this DM")

    # Find the dm's index in dms_details
    dms_index = 0
    while dms_index < len(data['dms_details']):
        if data['dms_details'][dms_index]['dm_id'] == dm_id:
            break
        dms_index += 1

    # Recursion to update dms_joined
    dm_members_index = 0
    while dm_members_index < len(data['dms_details'][dms_index]['members']):
        dms_joined_num_leave(data['dms_details'][dms_index]['members'][dm_members_index]['u_id'])
        dm_members_index += 1
    
    j = 0
    while j < len(dm_detail_info):
        if (dm_detail_info[j]['dm_id'] == dm_id):
            # remove the dm
            data['dms_details'].remove(dm_detail_info[j])
        j += 1
    
    data_store.set(data)

    return {

    }

def dm_list_v1(token):
    """An authorised user list out all the channels that he/she joined

    Arguments:
        token (string) - a token contains u_id, session_id and permission_id

    Exceptions:
        AccessError - Occurs when user type in an invalid id

    Return Value:
        list of dict: dms contains dict of channel_id and name
    """
    # check is the token passed in is valid, if not it will raise an access error
    is_valid_token(token)
    data = data_store.get()
    dm_detail = data['dms_details']
    user_id = decode_token(token)

    """ if (is_valid_user(user_id) == False):
        raise AccessError("Invalid user") """
    

    dm_list = []
    i = 0
    while i < len(dm_detail):
        dm_member = dm_detail[i]['members']
        j = 0
        while j < len(dm_member):
            if (user_id == dm_member[j]['u_id']):
                dm_list.append({
                    'dm_id': dm_detail[i]['dm_id'],
                    'name': dm_detail[i]['name']
                })
            j += 1
        i += 1
    
    return {
        'dms': dm_list
    }


# # Check token of authorised user is valid or not
# # Search information at data['emailpw']
# # If authorised user with invalid token then return False
# # If authorised user with valid token then return True
# def check_valid_token(token):
#     data = data_store.get()
#     emailpw = data['emailpw']
    
#     auth_user_id = jwt.decode(token, secret, algorithms=['HS256'])["u_id"]
#     user_session = jwt.decode(token, secret, algorithms=['HS256'])["session_id"]

#     user_element = 0
#     while user_element < len(emailpw):
#         if emailpw[user_element]['u_id'] == auth_user_id:
#             break
#         user_element += 1
    
#     session_id = emailpw[user_element]['session_id']
#     if user_session in session_id:
#         return True

#     return False
# #Finish authorised user valid token check

def is_valid_token(token):
    """ check if token is valid """
    
    secret = 'COMP1531'
    u_id = jwt.decode(token, secret, algorithms=['HS256'])['u_id']
    session_id = jwt.decode(token, secret, algorithms=['HS256'])['session_id']

    data = data_store.get()
    emailpw = data['emailpw']
    i = 0
    while i < len(emailpw):
        if (emailpw[i]['u_id'] == u_id):
            if (session_id in emailpw[i]['session_id']):
                return
        i += 1

    raise AccessError(description="Invalid token")

# dm messages function ==========================================================================
def dm_messages_v1(token, dm_id, start):
    """The function dm_messages_v1 returns up to 50 messages between the two indexes “start”
    and “start + 50 in a dm of which the authorised user is a member of.”
    
    Arguments:
        token (string) - ID of an authorised user.
        dm_id (integer) - ID of a valid dm.
        start (integer) – the starting index of a list of messages.

    Exceptions:
        InputError – Occurs when 'dm_id' does not refer to a valid dm
        and the 'start' is greater than the total amount of messages in the dm.
        AccessError – Occurs when the authorised user is not a member of the dm
        and the dm_id is valid.
    
    Return value:
        Returns 'messages' on the condition that the total messages is less than 50.
        Returns 'start' on all conditions.
        Returns 'start + 50' on the condition that total messages is greater than 50.
        Returns 'end' on all conditions.
    """
    # Accessing the data store
    data = data_store.get()
    dms = data["dms_details"]
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
        
    # Defining the end index
    end = int(start) + 50
        
    # Checks for exceptions
    check_valid_token(token)
    check_valid_dmid(dm_id)
    start_greater(dm_id, start)
    check_dm_member(dm_id, auth_user_id)

    # Otherwise, return the messages in the DM

    # Append all messages in a list
    message_list = []
    for i in range(len(dms)):
        if int(dms[i]['dm_id']) == int(dm_id):
            dm_messages = dms[i]['messages']
            for j in range(len(dm_messages)):
                message_list.append(dm_messages[j])
                
    message_list.reverse()
   
    if len(message_list) < 50:
        return { 
            'messages': message_list[int(start):int(end)], 
            'start': int(start),
            'end': -1 
        }
    else:
        return { 
            'messages': message_list[int(start):int(end)], 
            'start': start,
            'end': end 
        }
