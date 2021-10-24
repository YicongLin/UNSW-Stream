from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt

# helper functions ==============================================================================
from src.channel import check_valid_token


# Function to check if dm_id is valid 
secret = 'COMP1531'
def check_valid_dm_id(dm_id):

    data = data_store.get()
# ============================================================

# ===========(Raise errors and associate functions)===========
    dms_details_data = data['dms_details']
# ============================================================
    dms_members_element = 0

    all_dm_id = []
# ==================================
    while dms_members_element < len(dms_details_data):
# Check dm_id valid or not
        all_dms_id.append(dms_details_data[dms_members_element]['dm_id'])
# Serach information at data['dms_details']
        dms_members_element += 1
# If dm_id is invalid then return False

# If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dms_id_element = 0
def check_valid_dmid(dm_id):
    while dms_id_element < len(all_dms_id):
    data = data_store.get()
        if dm_id == all_dms_id[dms_id_element]:

            return dm_ids_element 
    dms_element = 0
        dms_id_element += 1
    all_dm_id = []

    while dms_element  < len(data['dms_details']):
    if dm_id not in all_dms_id:
        all_dm_id.append(data['dms_details'][dms_element]['dm_id'])
        return False
        dms_element += 1
            

    pass
    if dm_id not in all_dm_id :

        return False
# Function to check if user is a member of the dm 

def check_member_dm(dm_id_element, u_id):
    dm_id_element = 0
    data = data_store.get()
    while dm_id_element < len(all_dm_id):

        if dm_id == all_dm_id[dm_id_element]:
    members_in_dm = data['dms_details'][dm_id_element]['dm_members']
            return dm_id_element
    each_member_element = 0
        dm_id_element += 1
    each_member_id = []
            
    while each_member_element < len(members_in_dm):
    pass
        each_member_id.append(members_in_dm[each_member_element]['u_id'])
# Finish valid dm_id check
        each_member_element += 1 
# ==================================


    if u_id not in each_member_id:
# ==================================
        return False
# Check authorised user is an member of dm or not

# Serach information at data['dms_details'][dm_id_element]['dm_members']
    return each_member_id
# If authorised user is a not member of dm then return False

# If authorised user is a member of dm then return member_id_element (its index at dm_members[member_id_element])
# Function to check whether the start of messages is greater than 
def check_valid_dm_token(token, dm_id_element):
# the total number of messages or not
    data = data_store.get()
def start_greater_than_total(dm_id, start):

    data = data_store.get()
    decoded_token = decode_JWT(token)
    dms = data["dms_details"]
    auth_user_id = decoded_token["u_id"]
    

    # Finding the specific dm
    dm_members = data['dms_details'][dm_id_element]['members']
    count = 0
    all_members_id = []
    for i in range(len(dms)):
    member_id_element = 0
        if dm_id == dms[i]["dm_id"]:
    while member_id_element < len(dm_members):
            break
        all_members_id.append(dm_members[member_id_element]['u_id'])
        count += 1
        member_id_element += 1


    x = dms[count]
    if auth_user_id not in all_members_id:
    messages = x["messages"]
        return False
    if start <= len(messages):

        return False

# Function to check if dm_id is valid 
def check_valid_dm_id(dm_id):
    data = data_store.get()

    dms_details_data = data['dms_details']
    dms_members_element = 0
    all_dm_id = []
    while dms_members_element < len(dms_details_data):
        all_dms_id.append(dms_details_data[dms_members_element]['dm_id'])
        dms_members_element += 1

    dms_id_element = 0
    while dms_id_element < len(all_dms_id):
        if dm_id == all_dms_id[dms_id_element]:
            return dm_ids_element 
        dms_id_element += 1

    if dm_id not in all_dms_id:
        return False
            
    pass

# Function to check if user is a member of the dm 
def check_member_dm(dm_id_element, u_id):
    data = data_store.get()

    members_in_dm = data['dms_details'][dm_id_element]['dm_members']
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_dm):
        each_member_id.append(members_in_dm[each_member_element]['u_id'])
        each_member_element += 1 

    if u_id not in each_member_id:
        return False

    return each_member_id

# Function to check whether the start of messages is greater than 
# the total number of messages or not
def start_greater_than_total(dm_id, start):
    data = data_store.get()
    dms = data["dms_details"]
    
    # Finding the specific dm
    count = 0
    for i in range(len(dms)):
        if dm_id == dms[i]["dm_id"]:
            break
        count += 1

    x = dms[count]
    messages = x["messages"]
    if start <= len(messages):
        return False

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
    
#<<<<<<< HEAD
    # Raising an error if the given dm ID is not 
    # a valid dm in the created list
    is_valid_dm = check_valid_dm_id(dm_id)
    if is_valid_dm == False:
        raise InputError("Invalid dm_id")

#=======
    # Creating a list of valid dm IDS
    valid_dm_ids = []
    for i in range(len(dms)):
        valid_dm_ids.append(dms[i]["dm_id"])
    
    # Error raised if the given dm ID is not found in the list
    if dm_id not in valid_dm_ids:
        raise InputError("Invalid dm_id")
   
    # List of valid user IDS
    users = data["users"]
    valid_user_ids = []
    for i in range(len(users)):
        valid_user_ids.append(users[i]["u_id"])
       
    # Finding the specific dm
    count = 0
    for i in range(len(dms)):
        if dm_id == dms[i]["dm_id"]:
            break
        count += 1
       
#>>>>>>> master
    # Raising an error if start is greater than
    # the total number of messages in the given dm
    is_greater = start_greater_than_total(dm_id, start)
    if is_greater != False:
        raise InputError("Exceeded total number of messages in this dm") 
        
        
    # Raising an error if the authorised user 
    # is not a member of the valid dm
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']
    
    already_a_member = check_member_dm(dm_id, auth_user_id)
    if already_a_member == False:
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
    
def is_valid_user(u_id):

    data = data_store.get()
# dm messages function ==========================================================================
    user_dict = data['users']
def dm_messages_v1(token, dm_id, start):
    i = 0
    """The function dm_messages_v1 returns up to 50 messages between the two indexes “start”
    while i < len(user_dict):
    and “start + 50 in a dm of which the authorised user is a member of.”
        if (u_id == user_dict[i]):
    
            return True
    Arguments:
        i += 1
        token (string) - ID of an authorised user.
    return False
        dm_id (integer) - ID of a valid dm.

        start (integer) – the starting index of a list of messages.
def decode_token(token):

    secret = 'COMP1531'
    Exceptions:
    result = jwt.decode(token, secret, algorithms=['HS256'])['u_id']
        InputError – Occurs when 'dm_id' does not refer to a valid dm
    u_id = result
        and the 'start' is greater than the total amount of messages in the dm.
    return u_id
        AccessError – Occurs when the authorised user is not a member of the dm

        and the dm_id is valid.

    
# a function to check if the user in u_ids is a valid user
    Return value:
def check_user(u_ids):
        Returns 'messages' on the condition that the total messages is less than 50.
    data = data_store.get()
        Returns 'start' on all conditions.
    users_dict = data['users']
        Returns 'start + 50' on the condition that total messages is greater than 50.
    user_id_list = []
        Returns 'end' on all conditions.
    if (len(u_ids) >= 1):
    """
        a = 0
 # Accessing the data store
        while a < len(users_dict):
    data = data_store.get()
            user_id_list.append(users_dict[a]['u_id'])
    dms = data["dms_details"]
            a += 1

        b = 0
    # create the dictionary messages 
        while b < len(u_ids):
    messages = [ {
            if (u_ids[b] not in user_id_list):
        'message_id': '',
                return 0
        'u_id': '',
            b += 1
        'message': '',
    
        'time_created': '',
    return 1 
    } ]
 
    
# get the members details that on the list passed in
    # for each dm in dms details 
def get_member_detail(id_list):
    for i in range(len(dms)):
    data = data_store.get()
        # add messages dictionary into it 
    users_dict = data['users']
        dms[i]['messages'] = messages
    user_detail_list = []
        dms[i]['start'] = 0
    i = 0
        dms[i]['end'] = 50
    while i < len(id_list):
        
        j = 0
    # Defining the end index
        while j < len(users_dict):
        end = start + 50
            if (id_list[i] == users_dict[j]['u_id']):
    
                user_detail_list.append(users_dict[j])
#<<<<<<< HEAD
            j += 1
    # Raising an error if the given dm ID is not 
        i += 1
    # a valid dm in the created list
    return user_detail_list
    is_valid_dm = check_valid_dm_id(dm_id)

    if is_valid_dm == False:

        raise InputError("Invalid dm_id")
# get every users'handle_str and append them in a list

def get_name(id_list):
#=======
    data = data_store.get()
    # Creating a list of valid dm IDS
    users_dict = data['users']
    valid_dm_ids = []
    names_list = []
    for i in range(len(dms)):
    i = 0
        valid_dm_ids.append(dms[i]["dm_id"])
    while i < len(id_list):
    
        j = 0
    # Error raised if the given dm ID is not found in the list
        while j < len(users_dict):
    if dm_id not in valid_dm_ids:
            if (id_list[i] == users_dict[j]['u_id']):
        raise InputError("Invalid dm_id")
                names_list.append(users_dict[j]['handle_str'])
   
            j += 1
    # List of valid user IDS
        i += 1
    users = data["users"]
    names_list = sorted(names_list)
    valid_user_ids = []
    return names_list
    for i in range(len(users)):

        valid_user_ids.append(users[i]["u_id"])

       
def dm_remove_v1(token, dm_id):
    # Finding the specific dm
    if (is_valid_token(token) == False):
    count = 0
        raise AccessError("Invalid token")
    for i in range(len(dms)):
    
        if dm_id == dms[i]["dm_id"]:
    data = data_store.get()
            break
    dm_detail_info = data['dms_details']
        count += 1
    user_id = decode_token(token)
       
    
#>>>>>>> master
    
    # Raising an error if start is greater than
    # checking for both errors
    # the total number of messages in the given dm
    i = 0
    is_greater = start_greater_than_total(dm_id, start)
    input = 0
    if is_greater != False:
    access = 0
        raise InputError("Exceeded total number of messages in this dm") 
    while i < len(dm_detail_info):
        
        if (dm_detail_info[i]['dm_id'] == dm_id):
        
            input = 1
    # Raising an error if the authorised user 
            creator = dm_detail_info[i]['creator']
    # is not a member of the valid dm
            if (user_id == creator[0]['u_id']):
    SECRET = 'COMP1531'
                access = 1
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
        i += 1
    auth_user_id = decode_token['u_id']
    # didn't find the dm id in datastore
    
    if (input == 0):
    already_a_member = check_member_dm(dm_id, auth_user_id)
        raise InputError("Invalid DM ID")
    if already_a_member == False:

        raise AccessError("You are not a member of the dm")  
    # the user passed in is not the creator of this dm

    if (access == 0):
    # Append all messages in a list
        raise AccessError("Access denied, user is not a creator of this DM")
    message_list = []
    
    for message in messages:
    j = 0
        message_list.append(message["message"])
    while j < len(dm_detail_info):
   
        if (dm_detail_info[j]['dm_id'] == dm_id):
    if len(messages) < 50:
            # check if the user is the creator of this dm
        return { 
            creator = dm_detail_info[j]['creator']
            'messages': tuple(message_list)[start:end], 
            if (user_id == creator[0]['u_id']):
            'start': start,
                data['dms_details'].remove(dm_detail_info[j])
            'end': -1 
        j += 1
        }
    
    else:
    data_store.set(data)
        return { 

            'messages': tuple(message_list)[start:end], 
    return {
            'start': start,

            'end': end 
    }
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
