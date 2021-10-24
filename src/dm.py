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
    
