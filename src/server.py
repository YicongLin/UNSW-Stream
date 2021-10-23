import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.channel import check_valid_channel_id, check_valid_uid, check_member, channel_owners_ids, check_channel_owner_permissions, start_greater_than_total
from src.error import InputError
from src import config
from src.message import message_send_v1, message_edit_v1, message_remove_v1

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
    return dumps({
        'data': data
    })

@APP.route("/channel/messages/v2", methods=['GET'])
def messages():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")
        
    is_greater = start_greater_than_total(channel_id, start)
    if is_greater != False:
        raise InputError("Exceeded total number of messages in this channel")
        
    each_member_id = check_member(channel_id, u_id)
    if each_member_id  == False:
        raise InputError("User is not a member of this channel")
    
    messages = channel_messages_v2(token, channel_id, start)
    
    return dumps(messages)

@APP.route("/message/send/v1", methods = ['POST'])
def send_message():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")
    
    each_member_id = check_member(channel_id, u_id)
    if each_member_id  == False:
        raise InputError("User is not a member of this channel")


@APP.route("message/edit/v1", methods = ['PUT'])
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    u_id = request_data['u_id']


@APP.route("message/remove/v1", methods = ['DELETE'])
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

@APP.route("dm/messages/v1", methods = ['GET'])






#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
