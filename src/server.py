import sys
import signal
from json import dump, dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import AccessError, InputError
from src import config
from src.channel import channel_addowner_v1, channel_details_v2, channel_removeowner_v1, channel_invite_v2, channel_messages_v2, channel_join_v2, channel_leave_v1
from src.channel import check_valid_channel_id, check_valid_uid, check_member, channel_owners_ids, check_channel_owner_permissions, start_greater_than_total, check_valid_token
from src.channels import channels_listall_v2, channels_create_v2
from src.dm import dm_details_v1, dm_leave_v1
from src.dm import check_valid_dmid, check_valid_dm_token, check_user, dm_create_v1
from src.auth import auth_register_v2, auth_login_v2, check_name_length, check_password_length, check_valid_email, check_duplicate_email
from src.error import InputError
from src.message import valid_dm_id, valid_message_length, member, message_senddm_v1
from src.admin import valid_uid, only_global_owner, not_a_global_owner, is_valid_token, admin_userpermission_change_v1, admin_user_remove_v1
from src.users import users_all_v1, user_profile_setname_v1, user_profile_v1, user_profile_setemail_v1, user_profile_sethandle_v1, check_alpha_num, check_duplicate_handle, check_duplicate_email, check_handle, check_valid_email, check_name_length, token_check, check_password_length
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
from jwt import InvalidSignatureError, DecodeError, InvalidTokenError
from src.token_helpers import decode_JWT
from src.other import clear_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError(description="Invalid channel_id")
    
    if is_valid_token(token) == False:
        raise AccessError(description="Invalid token")
        
    if check_valid_uid(u_id) == False:
        raise InputError(description="Invalid user ID")
        
    each_member_id = check_member(channel_id_element, u_id)
    if each_member_id  != False:
        raise InputError(description="User is already a member of this channel")

    if check_member(channel_id_element, token) == False:
        raise AccessError(description="Not an member of channel") 
    
    channel_invite_v2(token, channel_id, u_id)
            
    return dumps({})
        
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']

    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError(description="Invalid channel_id")

    if is_valid_token(token) == False:
        raise AccessError(description="Invalid token")
        
    each_member_id = check_member(channel_id_element, token)
    channel_status = channel_status(channel_id)
    channel_owner_permissions = check_channel_owner_permissions(token, each_owner_id)
    if each_member_id != False:
        raise InputError(description="Already a member of this channel")
    elif channel_owner_permissions == False and channel_status == False:
        raise AccessError(description="Channel is private and you are not a global owner")

    channel_join_v2(token, channel_id)
            
    return dumps({})

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    try:
        channel_id_element = check_valid_channel_id(channel_id)
        if channel_id_element == False:
            raise InputError(description="Invalid channel_id")
        
        if is_valid_token(token) == False:
            raise AccessError(description="Invalid token")
            
        is_greater = start_greater_than_total(channel_id, start)
        if is_greater == True:
            raise InputError(description="Exceeded total number of messages in this channel")
            
        each_member_id = check_member(channel_id, u_id)
        if each_member_id  == False:
            raise InputError(description="User is not a member of this channel")
        
        messages = channel_messages_v2(token, channel_id, start)
            
        return dumps(messages)
    
    except (InvalidSignatureError, DecodeError, InvalidTokenError):
        raise AccessError

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    print("new")

    try:
        is_valid_channel = check_valid_channel_id(channel_id)
        if is_valid_channel == False:
            raise InputError(description="Invalid channel_id")
        
        if is_valid_token(token) == False:
            raise AccessError(description="Invalid token")
        
        already_a_member = check_member(channel_id, token)
        if already_a_member == False:
            raise AccessError(description="You are not a member of the channel")

        channel_leave_v1(token, channel_id)
            
        return dumps({})

    except (InvalidSignatureError, DecodeError, InvalidTokenError):
        raise AccessError

@APP.route('/channel/addowner/v1', methods=['POST'])
def add_owner():
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({})


@APP.route('/channel/removeowner/v1', methods=['POST'])
def remove_owner():
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({})

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details():

    token = request.args.get('token')
    channel_id = request.args.get('channel_id')

    channel_details = channel_details_v2(token, channel_id)

    return dumps(channel_details)



@APP.route('/channels/listall/v2', methods=['GET'])
def channels_listall():
    token = request.args.get('token')

    all_channels = channels_listall_v2(token)

    return dumps(all_channels)

@APP.route('/dm/details/v1', methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')

    try:
        dm = dm_details_v1(token, dm_id)

        return dumps(dm)

    except (InvalidSignatureError, DecodeError, InvalidTokenError):
            raise AccessError



@APP.route('/dm/leave/v1', methods=['POST'])
def dm_leave():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']

    dm_leave_v1(token, dm_id)

    return dumps({})

@APP.route('/auth/register/v2', methods=['POST'])
def auth_register_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']
    name_first = request_data['name_first']
    name_last = request_data['name_last']


    if check_name_length(name_first) == False:
        raise InputError(description="Invalid name length")

    if check_name_length(name_last) == False:
        raise InputError(description="Invalid name length")
    
    if check_password_length(password) == False:
        raise InputError(description="Invalid password length")
    
    if check_duplicate_email(email) == False:
        raise InputError(description="Duplicate email")
    
    if check_valid_email(email) == False:
        raise InputError(description="Invalid email")
    
    result = auth_register_v2(email, password, name_first, name_last)
    return dumps(result)

@APP.route('/auth/login/v2', methods=['POST'])
def auth_login_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']

    if check_valid_email(email) == False:
        raise InputError(description="Invalid email")
    
    result = auth_login_v2(email, password)
    return dumps(result)

@APP.route('/message/senddm/v1', methods=['POST'])
def message_senddm_http():
    request_data = request.get_json()

    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']
    try: 
        if valid_dm_id == False:
            raise InputError(description="Invalid DM")
        
        if is_valid_token(token) == False:
            raise AccessError(description="Invalid token")

        if valid_message_length == False:
            raise InputError(description="Invalid message length")

        if member == False:
            raise AccessError(description="Not a member of the DM")

        result = message_senddm_v1(token, dm_id, message)

        return dumps(result)

    except (InvalidSignatureError, DecodeError, InvalidTokenError):
        raise AccessError

@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_user_remove_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']
    try:

        if valid_uid(u_id) == False:
            raise InputError(description="Invalid user")

        if is_valid_token(token) == False:
            raise AccessError(description="Invalid token")

        if only_global_owner(token, u_id) == True:
            raise InputError(description="Cannot remove the only global owner")
        
        if not_a_global_owner(token) == True:
            raise AccessError(description="You are not a global owner")

        admin_user_remove_v1(token, u_id)

        return dumps({})

    except (InvalidSignatureError, DecodeError, InvalidTokenError):
        raise AccessError

@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_userpermission_change_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']

    try:
        if valid_uid(u_id) == False:
            raise InputError(description="Invalid user")
        
        if is_valid_token(token) == False:
            raise AccessError(description="Invalid token")

        if only_global_owner(token, u_id) == True and permission_id == 2:
            raise InputError(description="Cannot demote the only global owner")
        print('____________')
        print('permission id is')
        print(permission_id)
        print('____________')

        if permission_id not in [1,2]:
            raise InputError("Invalid permission ID")
        
        if not_a_global_owner(token) == True:
            raise InputError(description="You are not a global owner")
        
        admin_userpermission_change_v1(token, u_id, permission_id)

        return dumps([])

    except (InvalidSignatureError, DecodeError, InvalidTokenError):
        raise AccessError

@APP.route('/dm/remove/v1', methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    """ if (is_creator(token, dm_id) == False):
        raise AccessError("Access denied, user is not a creator of this DM")

    if (is_valid_dm(dm_id) == False):
        raise InputError("Invalid DM ID") """
    
    dm_remove_v1(token, dm_id)

    return dumps({})

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']
    u_ids = data['u_ids']
    #user_id = decode_token(token)
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    if (check_user(u_ids) == 0):
        raise InputError(description="There is 1 or more invalid ids, please check again")
    
    """ if (check_valid_token(token) == False):
        raise AccessError(description="Invalid user") """

    result = dm_create_v1(token, u_ids)
    return dumps(result)

@APP.route('/auth/logout/v1', methods=['POST'])
def auth_logout_http():
    request_data = request.get_json()
    token = request_data['token']
    
    if token_check(token) == False:
        raise AccessError(description="Invalid token")

    result = auth_logout_v1(token)
    return dumps(result)

@APP.route('/users/all/v1', methods=['GET'])
def users_all_http():
    token = request.args.get('token')

    if token_check(token) == False:
        raise AccessError(description="Invalid token")

    result = users_all_v1(token)
    return dumps(result)

@APP.route('/user/profile/v1', methods=['GET'])
def user_profile_http():
    token = request.args.get('token')
    u_id = request.args.get('u_id')

    if token_check(token) == False:
        raise AccessError(description="Invalid token")
    
    if u_id_check(token) == False:
        raise InputError(description="Invalid u_id")
    
    result = user_profile_v1(token, u_id)
    return dumps(result)

@APP.route('/user/profile/setname/v1', methods=['PUT'])
def user_profile_setname_http():
    request_data = request.get_json()

    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']


    if check_name_length(name_first) == False:
        raise InputError(description='Invalid first name')
    
    if check_name_length(name_last) == False:
        raise InputError(description='Invalid last name')
    
    if token_check(token) == False:
        raise AccessError(description="Invalid token")
    
    result = user_profile_setname_v1(token, name_first, name_last)
    return dumps(result)

@APP.route('/user/profile/setemail/v1', methods=['PUT'])
def user_profile_setemail_http():
    request_data = request.get_json()

    token = request_data['token']
    email = request_data['email']

    if token_check(token) == False:
        raise AccessError(description="Invalid token")
    
    if check_duplicate_email == False:
        raise InputError(description='Duplicate email')
    
    if check_valid_email(email) == False:
        raise InputError(description="Invalid email")

    result = user_profile_setemail_v1(token, email)
    return dumps(result)

@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def user_profile_sethandle_http():
    request_data = request.get_json()

    token = request_data['token']
    handle_str = request_data['handle_str']

    if check_handle == False: 
        raise InputError(description='Invalid handle')
    
    if check_alpha_num(handle_str) == False:
        raise InputError(description='Invalid handle length')
    
    if check_duplicate_handle == False:
        raise InputError(description='Duplicate handle')
    
    if token_check(token) == False:
        raise AccessError(description="Invalid token")

    result = user_profile_sethandle_v1(token, handle_str)
    return dumps(result)

@APP.route('/channels/create/v2', methods=['POST'])
def channels_create():
    data = request.get_json()
    token = data['token']
    name = data['name']
    is_public = data['is_public']
    """ if (check_valid_token(token) == False):
        raise AccessError("Invalid user") """
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    # check for invalid name
    if len(name) > 20:
        raise InputError(description="Invalid name: Too long")
    elif len(name) == 0:
        raise InputError(description="Invalid name: Too short")
    
    result = channels_create_v2(token, name, is_public)
    return dumps(result)

@APP.route('/channels/list/v2', methods=['GET'])
def channels_list():
    data = request.get_json()
    token = data['token']
    if (is_valid_token(token) == False):
        raise AccessError(description="Invalid token")
    
    result = channels_list_v2(token)
    return dumps(result)

@APP.route('/dm/list/v1', methods=['GET'])
def dm_list():
    data = request.get_json()
    token = data['token']
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    result = dm_list_v1(token)
    return dumps(result)

@APP.route('/clear/v1', methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
