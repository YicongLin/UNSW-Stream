from requests.api import request
from auth import auth_register_v2, auth_login_v2, check_name_length, check_duplicate_email, check_password_length, check_valid_email
from error import InputError

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
    
    if check_password_length(password == False):
        raise InputError(description="Invalid password length")
    
    if check_duplicate_email(email) == False:
        raise InputError(description="Duplicate email")
    
    if check_valid_email(email) == False:
        raise InputError(description="Invalid email")

    return dumps(auth_register_v2(email, password, name_first, name_last)
)

@APP.route('/auth/login/v2', methods=['POST'])
def auth_login_http():
    request_data = request.get_json()

    email = request_data['email']
    password = request_data['password']

    if check_valid_email(email) == False:
        raise InputError(description="Invalid email")

    return dumps(auth_login_v2(email, password))

@APP.route('/users/all/v1', methods=['GET'])
def users_all_v1():
    request_data = request.get_json()

    token = request_data['token']





@APP.route('/user/profile/v1', methods=['GET'])


@APP.route('/user/profile/setname/v1', methods=['PUT'])


@APP.route('/user/profile/setemail/v1', methods=['PUT'])


@APP.route('/user/profile/sethandle/v1', methods=['PUT'])


