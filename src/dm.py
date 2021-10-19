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