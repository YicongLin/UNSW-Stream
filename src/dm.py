from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt

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
# If authorised user is a 
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
            return member_id_element
        member_id_element += 1

    if user_id not in all_members_id:
        return False

    pass
# ==================================


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


def dm_leave_v1(token, dm_id):
    data = data_store.get()

    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError("Invalid dm_id")

    member_id_element = check_valid_dm_token(token, dm_id_element)
    if member_id_element == False:
        raise AccessError("Login user has not right to access this dm")

    leave_dm_member['u_id'] = data['dms_details'][dm_id_element]['dm_members'][member_id_element]
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
>>>>>>> 4296dbb95b969195bed254a538d6a3ce59ea8fdf
