from _pytest.python_api import raises
from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.channel import check_valid_token

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
    data = data_store.get()

    dm_id = int(dm_id)
    dms_element = 0
    all_dm_id = []
    while dms_element  < len(data['dms_details']):
        all_dm_id.append(data['dms_details'][dms_element]['dm_id'])
        dms_element += 1

    if dm_id not in all_dm_id :
        return False

    dm_id_element = 0
    while dm_id_element < len(all_dm_id):
        if dm_id == all_dm_id[dm_id_element]:
            return dm_id_element
        dm_id_element += 1
            
    pass
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
        return False

    return each_member_id
# Finish  authorised user member check
# ==================================

# ==================================
# Check whether the start of messages is greater than 
# the total number of messages or not.
# Returns true if start is greater. 
def start_greater(dm_id, start):
    data = data_store.get()
    dms = data["dms_details"]
    
    for i in range(len(dms)):
        if dm_id == dms[i]["dms_id"]:
            x = dms[i]
            messages = x["messages"]
            if start > len(messages):
                return True
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
        if dms[i]["dm_id"] == dm_id:
            break
        dm_count += 1

    members = dms[dm_count]['members']
    member_list = []
    for i in range(len(members)):
        member_list.append(members[i]['u_id'])

    if u_id not in member_list:
        return False

    return each_member_id
# Finish DM member check
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
    if check_valid_token(token) == False:
        raise AccessError("Invalid token")

    # Raise a InputError if authorised user type in invalid dm_id
    # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    auth_user_id = decode_JWT(token)['u_id']
    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    if check_valid_dm_token(auth_user_id, dm_id_element) == False:
        raise AccessError("Login user has not right to access dm_details")

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
    if check_valid_token(token) == False:
        raise AccessError("Invalid token")

    # Raise a InputError if authorised user type in invalid dm_id
    # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    auth_user_id = decode_JWT(token)['u_id']
    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    # If authorised user is a member of dm then return member_id_element (its index at dm_members[member_id_element])
    each_member_id = check_valid_dm_token(auth_user_id, dm_id_element)
    if each_member_id == False:
        raise AccessError("Login user has not right to access this dm")

    # Find out the index of auth_user within dm['members']
    member_id_element = 0
    while member_id_element < len(each_member_id):
        if data['dms_details'][dm_id_element]['members'][member_id_element]['u_id'] == auth_user_id:
            break
        member_id_element += 1

    # Pick out dict from dm's members and then delete it 
    leave_dm_member = data['dms_details'][dm_id_element]['members'][member_id_element]
    data['dms_details'][dm_id_element]['members'].remove(leave_dm_member)

    return {}

def dm_create_v1(token, u_ids):
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
        
    data = data_store.get()
    dm = data['dms_details']
    user_id = decode_token(token)

    """ if (check_valid_token(token) == False):
        raise AccessError("Invalid user") """
    
    if (check_user(u_ids) == 0):
        raise InputError("There is 1 or more invalid ids, please check again")
    
    creator_detail = get_member_detail([user_id])
    
    new_dm_id = len(dm) + 1
    u_ids.append(user_id)
    handle_str = get_name(u_ids)
    member_detail = get_member_detail(u_ids)

    dm_detail_dict = {
        'dm_id': new_dm_id,
        'name': handle_str,
        'members': member_detail,
        'creator': creator_detail
    }
    
    data['dms_details'].append(dm_detail_dict)
    data_store.set(data)
    return {
        'dm_id': new_dm_id
    }

def is_valid_user(u_id):
    data = data_store.get()
    user_dict = data['users']
    i = 0
    while i < len(user_dict):
        if (u_id == user_dict[i]):
            return True
        i += 1
    return False

def decode_token(token):
    secret = 'COMP1531'
    result = jwt.decode(token, secret, algorithms=['HS256'])['u_id']
    u_id = result
    return u_id


# a function to check if the user in u_ids is a valid user
def check_user(u_ids):
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
                return 0
            b += 1
    
    return 1 
 
# get the members details that on the list passed in
def get_member_detail(id_list):
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


# get every users'handle_str and append them in a list
def get_name(id_list):
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
    return names_list


def dm_remove_v1(token, dm_id):
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    
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
        raise InputError("Invalid DM ID")

    # the user passed in is not the creator of this dm
    if (access == 0):
        raise AccessError("Access denied, user is not a creator of this DM")
    
    j = 0
    while j < len(dm_detail_info):
        if (dm_detail_info[j]['dm_id'] == dm_id):
            # check if the user is the creator of this dm
            creator = dm_detail_info[j]['creator']
            if (user_id == creator[0]['u_id']):
                data['dms_details'].remove(dm_detail_info[j])
        j += 1
    
    data_store.set(data)

    return {

    }

def dm_list_v1(token):
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
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


# Check token of authorised user is valid or not
# Search information at data['emailpw']
# If authorised user with invalid token then return False
# If authorised user with valid token then return True
def check_valid_token(token):
    data = data_store.get()
    emailpw = data['emailpw']
    
    auth_user_id = jwt.decode(token, secret, algorithms=['HS256'])["u_id"]
    user_session = jwt.decode(token, secret, algorithms=['HS256'])["session_id"]

    user_element = 0
    while user_element < len(emailpw):
        if emailpw[user_element]['u_id'] == auth_user_id:
            break
        user_element += 1
    
    session_id = emailpw[user_element]['session_id']
    if user_session in session_id:
        return True

    return False
#Finish authorised user valid token check

def is_valid_token(token):
    secret = 'COMP1531'
    u_id = jwt.decode(token, secret, algorithms=['HS256'])['u_id']
    session_id = jwt.decode(token, secret, algorithms=['HS256'])['session_id']

    data = data_store.get()
    emailpw = data['emailpw']
    i = 0
    while i < len(emailpw):
        if (emailpw[i]['u_id'] == u_id):
            if (session_id in emailpw[i]['session_id']):
                return True
        i += 1
    return False

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

    # Extracting the authorised user's ID from the token
    decoded_token = decode_JWT(token)
    auth_user_id = decode_token['u_id']

    # create the dictionary messages 
    messages = [ {
        'message_id': '',
        'u_id': '',
        'message': '',
        'time_created': '',
    } ]
    
    # for each dm in dms details 
    for i in range(len(dms)):
        # add messages dictionary into it 
        dms[i]['messages'] = messages
        dms[i]['start'] = 0
        dms[i]['end'] = 50
        
    # Defining the end index
        end = start + 50
    
    # Raising an error if the given dm ID is not a valid dm
    if check_valid_dmid(dm_id) == False:
        raise InputError("Invalid dm_id")
       
    # Finding the specific dm
    dm_count = 0
    for i in range(len(dms)):
        if dm_id == dms[i]["dm_id"]:
            break
        dm_count += 1
       
    # Raising an error if start is greater than
    # the total number of messages in the given dm
    if start_greater != True:
        raise InputError("Exceeded total number of messages in this dm") 
        
    # Raising an error if the authorised user 
    # is not a member of the valid dm
    if check_dm_member(dm_id, auth_user_id) == False:
        raise AccessError("You are not a member of the dm")  

    # Append all messages in a list
    message_list = []
    for message in messages:
        message_list.append(message["message"])
   
    if len(messages) < 50:
        return { 
            'messages': tuple(message_list)[start:end], 
            'start': start,
            'end': -1 
        }
    else:
        return { 
            'messages': tuple(message_list)[start:end], 
            'start': start,
            'end': end 
        }