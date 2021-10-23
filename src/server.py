import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.channel import channel_addowner_v1
from src.channel import check_valid_channel_id, check_valid_uid, check_member, check_exist_owner, check_permissions
from src.channel import check_not_owner, check_only_owner, channel_removeowner_v1
from src.dm import dm_details_v1, dm_create_v1
from src.dm import check_valid_dmid, check_valid_dm_token, check_user, decode_token, is_valid_user
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
        raise InputError(description="Invalid channel_id")

    if check_valid_uid(u_id) == False:
        raise InputError(description="Invalid user ID")

    new_owner_element = check_member(channel_id_element, u_id)
    if new_owner_element == False:
        raise InputError(description="User is not a member of this channel")
    
    each_owner_id = check_exist_owner(channel_id_element, u_id)
    if each_owner_id == False:
        raise InputError(description="User already is an owner of channel")
    
    if check_permissions(token, each_owner_id) == False:
        raise AccessError(description="No permissions to add user")

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
        raise InputError(description="Invalid channel_id")

    if check_valid_uid(u_id) == False:
        raise InputError(description="Invalid user ID")

    each_owner_id = check_not_owner(channel_id_element, u_id)
    if each_owner_id == False:
        raise InputError(description="User is not an owner of channel")

    if check_only_owner(channel_id_element, u_id) == False:
        raise InputError(description="User is the only owner of channel")

    if check_permissions(token, each_owner_id) == False:
        raise AccessError(description="No permissions to remove user")

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({})

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

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']
    u_ids = data['u_ids']
    user_id = decode_token(token)
    
    if (check_user(u_ids) == 0):
        raise InputError(description="There is 1 or more invalid ids, please check again")
    
    if (is_valid_user(user_id) == False):
        raise AccessError(description="Invalid user")

    result = dm_create_v1(token, u_ids)
    return dumps(result)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
