import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import AccessError, InputError
from src import config
from src.auth import auth_register_v2, auth_login_v2, check_name_length, check_password_length, check_valid_email, check_duplicate_email
from src.users import users_all_v1, user_profile_setname_v1, user_profile_v1, user_profile_setemail_v1, user_profile_sethandle_v1, check_alpha_num, check_duplicate_handle, check_duplicate_email, check_handle, check_valid_email, check_name_length, token_check
from src.error import InputError

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

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
