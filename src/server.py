import sys
import signal
from json import dump, dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import AccessError, InputError
from src import config
from src.channel import channel_addowner_v1, channel_details_v2, channel_removeowner_v1
from src.channel import check_valid_channel_id, check_valid_uid, check_member, channel_owners_ids, check_channel_owner_permissions
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.dm import dm_details_v1, dm_leave_v1, dm_create_v1, dm_remove_v1, dm_list_v1
from src.dm import check_valid_dmid, check_valid_dm_token, decode_token, check_user, is_valid_token
from src.auth import auth_register_v2, auth_login_v2, check_name_length, check_password_length, check_valid_email, check_duplicate_email
from src.error import InputError
from src.users import users_all_v1, user_profile_setname_v1, user_profile_v1, user_profile_setemail_v1, user_profile_sethandle_v1, check_alpha_num, check_duplicate_handle, check_duplicate_email, check_handle, check_valid_email, check_name_length, token_check, check_password_length
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
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

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({})


@APP.route('/channel/addowner/v1', methods=['POST'])
def add_owner():
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    if check_valid_uid(u_id) == False:
        raise InputError("Invalid user ID")

    each_member_id = check_member(channel_id_element, u_id)
    if each_member_id  == False:
        raise InputError("User is not a member of this channel")
    
    each_owner_id = channel_owners_ids(channel_id_element)

    if u_id in each_owner_id:
        raise InputError("User already is an owner of channel")
    
    if check_channel_owner_permissions(token, each_owner_id) == False:
        raise AccessError("No permissions to add user")

    channel_addowner_v1(token, channel_id, u_id)

    return dumps({})

@APP.route('/channel/removeowner/v1', methods=['POST'])
def remove_owner():
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    if check_valid_uid(u_id) == False:
        raise InputError("Invalid user ID")

    each_owner_id = channel_owners_ids(channel_id_element)

    if u_id not in each_owner_id:
        raise InputError("User is not an owner of channel")

    if u_id in each_owner_id and len(each_owner_id) == 1:
        raise InputError("User is the only owner of channel")

    if check_channel_owner_permissions(token, each_owner_id) == False:
        raise AccessError("No permissions to remove user")

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({})

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']

    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    if check_member(channel_id_element, token) == False:
        raise AccessError("Not an member of channel")

    channel_details = channel_details_v2(token, channel_id)

    return dumps(channel_details)

@APP.route('/channels/listall/v2', methods=['GET'])
def channels_listall():
    request_data = request.get_json()
    token = request_data['token']

    all_channels = channels_listall_v2(token)

    return dumps(all_channels)


@APP.route('/dm/details/v1', methods=['GET'])
def dm_details():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']

    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError(description="Invalid dm_id")

    if check_valid_dm_token(token, dm_id_element) == False:
        raise AccessError(description="Login user has not right to access dm_details")

    dm = dm_details_v1(token, dm_id)

    return dumps(dm)


@APP.route('/dm/leave/v1', methods=['POST'])
def dm_leave():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']

    dm_id_element = check_valid_dmid(dm_id)
    if dm_id_element == False:
        raise InputError(description="Invalid dm_id")

    if check_valid_dm_token(token, dm_id_element) == False:
        raise AccessError(description="Login user has not right to access this dm")

    dm_leave_v1(token, dm_id)

    return dumps({})


@APP.route('/auth/register/v2', methods=['POST'])
def auth_register_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']
    name_first = request_data['name_first']
    name_last = request_data['name_last']

    result = auth_register_v2(email, password, name_first, name_last)
    return dumps(result)

@APP.route('/auth/login/v2', methods=['POST'])
def auth_login_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']
    
    result = auth_login_v2(email, password)
    return dumps(result)


@APP.route('/dm/remove/v1', methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    
    dm_remove_v1(token, dm_id)

    return dumps({})

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']
    u_ids = data['u_ids']
    

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
    
    if check_valid_email == False:
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
    
    if check_duplicate_handle == False:
        raise InputError(description='Duplicate handle')
    
    if check_alpha_num(handle_str) == False:
        raise InputError(description='Invalid handle length')
    
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
    
    result = channels_create_v2(token, name, is_public)
    return dumps(result)

@APP.route('/channels/list/v2', methods=['GET'])
def channels_list():
    data = request.get_json()
    # token = data['token']
    token = request.args.get('token')


    
    result = channels_list_v2(token)
    return dumps(result)

@APP.route('/dm/list/v1', methods=['GET'])
def dm_list():
    
    
    token = request.args.get('token')
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