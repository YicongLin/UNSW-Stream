import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.channel import channel_addowner_v1, channel_details_v2, channel_removeowner_v1
from src.channel import check_valid_channel_id, check_valid_uid, check_member, channel_owners_ids, check_channel_owner_permissions, start_greater_than_total
from src.channels import channels_listall_v2
from src.dm import dm_details_v1, dm_leave_v1
from src.dm import check_valid_dmid, check_valid_dm_token
from src.auth import auth_register_v2, auth_login_v2, check_name_length, check_password_length, check_valid_email, check_duplicate_email
from src.error import InputError
from src.message import valid_dm_id, valid_message_length, member
from src.admin import valid_uid, only_global_owner, not_a_global_owner, valid_permission_id

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
  
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError(description="Invalid channel_id")
        
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
    u_id = request_data['u_id']
    
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError(description="Invalid channel_id")
        
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
    
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError(description="Invalid channel_id")
        
    is_greater = start_greater_than_total(channel_id, start)
    if is_greater == True:
        raise InputError(description="Exceeded total number of messages in this channel")
        
    each_member_id = check_member(channel_id, u_id)
    if each_member_id  == False:
        raise InputError(description="User is not a member of this channel")
    
    messages = channel_messages_v2(token, channel_id, start)
    
    return dumps(messages)

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    
    is_valid_channel = check_valid_channel_id(channel_id)
    if is_valid_channel == False:
        raise InputError(description="Invalid channel_id")
    
    already_a_member = check_member(channel_id, auth_user_id)
    if already_a_member == False:
        raise AccessError(description="You are not a member of the channel")
    
    channel_leave_v1(token, channel_id)
    
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

    if valid_dm_id == False:
        raise InputError(description="Invalid DM")

    if valid_message_length == False:
        raise InputError(description="Invalid message length")

    if member == False:
        raise AccessError(description="Not a member of the DM")

    result = message_senddm_v1(token, dm_id, message)

    return dumps(result)

@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_user_remove_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']

    if valid_uid(u_id) == False:
        raise InputError(description="Invalid user")

    if only_global_owner(u_id) == True:
        raise InputError(description="Cannot remove the only global owner")
    
    if not_a_global_owner(token) == True:
        raise AccessError(description="You are not a global owner")

    admin_user_remove_v1(token, u_id)

    return dumps({})

@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_userpermission_change_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permissions_id']

    if valid_uid(u_id) == False:
        raise InputError(description="Invalid user")

    if only_global_owner(u_id) == True and permission_id == 2:
        raise InputError(description="Cannot demote the only global owner")
    
    if valid_permission_id(permission_id) == False:
        raise InputError(description="Invlid permission ID")

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
