import sys
import signal
from json import dump, dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import AccessError, InputError
from src import config
from src.channel import channel_addowner_v1, channel_details_v2, channel_removeowner_v1, channel_join_v2, channel_invite_v2, channel_messages_v2, channel_leave_v1
from src.channels import channels_listall_v2, channels_create_v2, channels_list_v2
from src.dm import dm_details_v1, dm_leave_v1, dm_create_v1, dm_list_v1, dm_remove_v1, dm_messages_v1
from src.auth import auth_register_v2, auth_login_v2, check_name_length, check_password_length, check_valid_email, check_duplicate_email
from src.message import message_senddm_v1, message_send_v1, message_edit_v1, message_remove_v1, message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.users import users_all_v1, user_profile_setname_v1, user_profile_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
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

    result = channel_invite_v2(token, channel_id, u_id)
            
    return dumps(result)
        
@APP.route('/channel/join/v2', methods=['POST'])
def channel_join_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']

    result = channel_join_v2(token, channel_id)
            
    return dumps(result)

@APP.route('/channel/messages/v2', methods=['GET'])
def channel_messages_http():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    
    result = channel_messages_v2(token, channel_id, start)
            
    return dumps(result)

@APP.route('/channel/leave/v1', methods=['POST'])
def channel_leave_http():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']

    result = channel_leave_v1(token, channel_id)
            
    return dumps(result)

@APP.route('/channel/addowner/v1', methods=['POST'])
def add_owner():
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_addowner_v1(token, channel_id, u_id)

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

    dm = dm_details_v1(token, dm_id)

    return dumps(dm)

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

    result = auth_register_v2(email, password, name_first, name_last)
    return dumps(result)

@APP.route('/auth/login/v2', methods=['POST'])
def auth_login_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']
    
    result = auth_login_v2(email, password)
    return dumps(result)

@APP.route('/message/senddm/v1', methods=['POST'])
def message_senddm_http():
    request_data = request.get_json()

    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']

    result = message_senddm_v1(token, dm_id, message)

    return dumps(result)

@APP.route("/message/send/v1", methods = ['POST'])
def send_message():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']

    result = message_send_v1(token, channel_id, message)

    return dumps(result)

@APP.route("/message/edit/v1", methods = ['PUT'])
def edit_message():  
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    message = request_data['message']

    result = message_edit_v1(token, message_id, message)

    return dumps(result)

@APP.route("/message/remove/v1", methods = ['DELETE'])
def remove_message(): 
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    
    result = message_remove_v1(token, message_id)

    return dumps(result)

@APP.route("/message/react/v1", methods = ['POST'])
def react_message():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']

    message_react_v1(token, message_id, react_id)

    return dumps({})

@APP.route("/message/unreact/v1", methods = ['POST'])
def unreact_message():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']

    message_unreact_v1(token, message_id, react_id)

    return dumps({})

@APP.route("/message/pin/v1", methods = ['POST'])
def pin_message():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

    message_pin_v1(token, message_id)

    return dumps({})

@APP.route("/message/unpin/v1", methods = ['POST'])
def unpin_message():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

    message_unpin_v1(token, message_id)

    return dumps({})

@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_user_remove_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']

    admin_user_remove_v1(token, u_id)

    return dumps({})


@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_userpermission_change_http():
    request_data = request.get_json()

    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']
        
    result = admin_userpermission_change_v1(token, u_id, permission_id)

    return dumps(result)

@APP.route('/dm/remove/v1', methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    
    dm_remove_v1(token, dm_id)

    return dumps({})

@APP.route('/dm/messages/v1', methods=['GET'])
def dm_messages_http():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')

    result = dm_messages_v1(token, dm_id, start)

    return dumps(result)

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

    result = auth_logout_v1(token)
    return dumps(result)

@APP.route('/users/all/v1', methods=['GET'])
def users_all_http():
    token = request.args.get('token')

    result = users_all_v1(token)
    return dumps(result)

@APP.route('/user/profile/v1', methods=['GET'])
def user_profile_http():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    
    result = user_profile_v1(token, u_id)
    return dumps(result)

@APP.route('/user/profile/setname/v1', methods=['PUT'])
def user_profile_setname_http():
    request_data = request.get_json()

    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']

    result = user_profile_setname_v1(token, name_first, name_last)
    return dumps(result)

@APP.route('/user/profile/setemail/v1', methods=['PUT'])
def user_profile_setemail_http():
    request_data = request.get_json()

    token = request_data['token']
    email = request_data['email']

    result = user_profile_setemail_v1(token, email)
    return dumps(result)

@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def user_profile_sethandle_http():
    request_data = request.get_json()

    token = request_data['token']
    handle_str = request_data['handle_str']

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