from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt
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
    dms_details_data = data['dms_details']
    dms_element = 0
    all_dm_id = []
    while dms_element  < len(dms_details_data):
        all_dm_id.append(dms_details_data[dms_element]['dm_id'])
        dms_element  += 1

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
def check_valid_dm_token(token, dm_id_element):
    data = data_store.get()

    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    u_id = decode_token['u_id']

    dm_members = data['dms_details'][dm_id_element]['dm_members']
    all_members_id = []

    member_id_element = 0
    while member_id_element < len(dm_members):
        all_members_id.append(dm_members[member_id_element]['u_id'])
        if u_id == dm_members[member_id_element]['u_id']:
            return member_id_element
        member_id_element += 1

    if u_id not in all_members_id:
        return False

    pass
# Finish  authorised user member check
# ==================================


# ============================================================
# =====================(Actual functions)=====================
# ============================================================

def dm_details_v1(token, dm_id):
    data = data_store.get()

    # Raise a InputError if authorised user type in invalid dm_id
    # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    if check_valid_dm_token(token, dm_id_element) == False:
        raise AccessError("Login user has not right to access dm_details")

    # Pick out dm name and its members from data['dms_details'][dm_id_element]
    name = data['dms_details'][dm_id_element]['name']
    members = data['dms_details'][dm_id_element]['dm_members']

    return {
        'name': name,
        'members': members
    }


def dm_leave_v1(token, dm_id):
    data = data_store.get()

     # Raise a InputError if authorised user type in invalid dm_id
     # If dm_id is valid then return dm_id_element (its index at dms_details_data[dms_element])
    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    # Raise an AccessError if authorised user type in a valid dm_id
    # but the authorised user is not a member of dm
    # If authorised user is a member of dm then return member_id_element (its index at dm_members[member_id_element])
    member_id_element = check_valid_dm_token(token, dm_id_element)
    if member_id_element == False:
        raise AccessError("Login user has not right to access this dm")


    # Pick out dict from dm's members and then delete it 
    leave_dm_member = data['dms_details'][dm_id_element]['dm_members'][member_id_element]
    data['dms_details'][dm_id_element]['dm_members'].remove(leave_dm_member)

    return {}


def dm_create_v1(token, u_ids):
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
    global secret
    result = jwt.decode(token, secret, algorithms=['HS256'])
    u_id = result['u_id']
    return u_id


# a function to check if the user in u_ids is a valid user
def check_user(u_ids):
    data = data_store.get()
    users_dict = data['users']
    user_id_list = []
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
    data = data_store.get()
    dm_detail_info = data['dms_details']
    user_id = decode_token(token)
    
    if (is_creator(user_id, dm_id) == False):
        raise AccessError("Access denied, user is not a creator of this DM")
    
    if (is_valid_dm(dm_id) == False):
        raise InputError("Invalid DM ID")

    
    j = 0
    while j < len(dm_detail_info):
        if (dm_detail_info[j]['dm_id'] == dm_id):
            # check if the user is the creator of this dm
            creator = dm_detail_info[j]['creator']
            if (user_id == creator['u_id']):
                data['dms_details'].remove(dm_detail_info[j])
        j += 1
    
    data_store.set(data)

    return {

    }

def dm_list_v1(token):
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

# check if the dm id is valid
def is_valid_dm(dm, id):
    i = 0
    while i < len(dm):
        if (dm[i]['dm_id'] == id):
            return True
        i += 1
    return False

# Check token of authorised user is valid or not
# Search information at data['emailpw']
# If authorised user with invalid token then return False
# If authorised user with valid token then return True
def check_valid_token(token):
    data = data_store.get()

    
    auth_user_id = decode_JWT(token)["u_id"]
    user_session = decode_JWT(token)["session_id"]

    user_element = 0
    while user_element < len(data['emailpw']):
        if data['emailpw'][user_element]['u_id'] == auth_user_id:
            break
        user_element += 1
    
    session_id = data['emailpw'][user_element]['session_id']
    if user_session in session_id:
        return True

    return False
#Finish authorised user valid token check

def decode_JWT(token):
    return jwt.decode(token, secret, algorithms=['HS256'])

def is_creator(token, dm_id):
    data = data_store.get()
    dm_detail = data['dms_details']
    u_id = decode_token(token)
    i = 0
    while i < len(dm_detail):
        if (dm_detail[i]['dm_id'] == dm_id):
            # check if the user is the creator of this dm
            creator = dm_detail[i]['creator']
            if (u_id == creator['u_id']):
                return True
        i += 1
    return False