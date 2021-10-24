from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt

secret = 'COMP1531'
# Raise Errors check for dm_details_v1
# ==================================
# Check Invalid dm_id
# If dm_id is valid then return its index
def check_valid_dmid(dm_id):
    data = data_store.get()
    dms_details_data = data['dms_details']
    dms_element = 0
    all_dm_id = []
    while dms_element  < len(dms_details_data):
        all_dm_id.append(dms_details_data[dms_element]['dm_id'])
        dms_element  += 1

    dm_id_element = 0
    while dm_id_element < len(all_dm_id):
        if dm_id == all_dm_id[dm_id_element]:
            return dm_id_element
        dm_id_element += 1

    if dm_id not in all_dm_id :
        return False
            
    pass
# Finish valid dm_id check
# ==================================
# Check token user is an member of dm
def check_valid_dm_token(token, dm_id_element):
    data = data_store.get()

    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    user_id = decode_token['u_id']

    dm_members = data['dms_details'][dm_id_element]['dm_members']
    all_members_id = []

    member_id_element = 0
    while member_id_element < len(dm_members):
        all_members_id.append(dm_members[member_id_element]['u_id'])
        if user_id == dm_members[member_id_element]['u_id']:
            return True
        member_id_element += 1

    if user_id not in all_members_id:
        return False

    pass
# ==================================
# ==================================






def dm_details_v1(token, dm_id):
    data = data_store.get()

    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    if check_valid_dm_token(token, dm_id_element) == False:
        raise AccessError("Login user has not right to access dm_details")

    name = data['dms_details'][dm_id_element]['name']
    members = data['dms_details'][dm_id_element]['dm_members']

    return {
        'name': name,
        'members': members
    }

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

def decode_token(token):
    global secret
    result = jwt.decode(token, secret, algorithms=['HS256'])
    u_id = result['u_id']
    return u_id

def is_valid_user(u_id):
    data = data_store.get()
    user_dict = data['users']
    i = 0
    while i < len(user_dict):
        if (u_id == user_dict[i]):
            return True
        i += 0
    return False