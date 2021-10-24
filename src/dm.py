from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.channel import check_valid_token

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

    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token["u_id"]

    dm_members = data['dms_details'][dm_id_element]['dm_members']
    all_members_id = []

    member_id_element = 0
    while member_id_element < len(dm_members):
        all_members_id.append(dm_members[member_id_element]['u_id'])
        if auth_user_id == dm_members[member_id_element]['u_id']:
            return member_id_element
        member_id_element += 1

    if auth_user_id not in all_members_id:
        return False

    pass
# Finish  authorised user member check
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
    users = data['users']
    dm = data['dms']

    if (check_user(users, u_ids) == 0):
        raise InputError("There is 1 or more invalid ids, please check again")
    
    new_dm_id = len(dm) + 1

    handle_str = get_name(users, u_ids)
    member_detail = get_member_detail(users, u_ids)

    dm_detail_dict = {
        'dm_id': new_dm_id,
        'name': handle_str,
        'members': member_detail
    }

    dms_dict = {
        'dm_id': new_dm_id,
        'name': handle_str
    }

    data['dms'].append(dms_dict)
    data['dms_details'].append(dm_detail_dict)
    return {
        'dm_id': new_dm_id
    }

# a function to check if the user in u_ids is a valid user
def check_user(auth_users, u_ids):
    """ i = 0
    
    while i < len(u_ids):
        j = 0
        flag = 0
        while j < len(auth_users):
            if (u_ids[i] == auth_users[j]['u_id']):
                flag == 1
            j += 1
        if (flag == 0):
            return 0
        i += 1
    
    return 1 """
    user_id_list = []
    a = 0
    while a < len(auth_users):
        user_id_list.append(auth_users[a]['u_id'])
        a += 1
    b = 0
    while b < len(u_ids):
        if (u_ids[b] not in user_id_list):
            return 0
        b += 1
    return 1 
# get the members details that on the list passed in
def get_member_detail(users_dict, id_list):
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
def get_name(users_dict, id_list):
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
    dm_info = data['dms']
    dm_detail_info = data['dms_details']
    if (is_valid_dm(dm_info, dm_id) == False):
        raise InputError("Invalid DM ID")
    
    i = 0
    while i < len(dm_info):
        if (dm_info[i]['dm_id'] == dm_id):
            data['dms'].remove(dm_info[i])
        i += 1

    j = 0
    while j < len(dm_detail_info):
        if (dm_detail_info[j]['dm_id'] == dm_id):
            data['dms_details'].remove(dm_detail_info[j])
        j += 1
    


    return {

    }
# check if the dm id is valid
def is_valid_dm(dm, id):
    i = 0
    while i < len(dm):
        if (dm[i]['dm_id'] == id):
            return True
        i += 1
    return False