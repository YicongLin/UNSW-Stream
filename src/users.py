import re 
import json
import jwt
from werkzeug.exceptions import RequestedRangeNotSatisfiable
from src.data_store import data_store
from src.error import InputError, AccessError
from src.token_helpers import decode_JWT

# HELPER FUNCTIONS 
def token_check(token):
    store = data_store.get()
    decoded_token = decode_JWT(token)
    
    found = False 
    i = 0
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        # check if session id matches any current session id’s 
        if decoded_token['session_id'] in user['session_id']:
            found = True

        i += 1 

    if found == False:
        return False
    
    pass

def check_handle(handle_str):
    if len(handle_str) < 3 or len(handle_str) > 20:
        return False

    pass

def check_duplicate_handle(handle_str):
    store = data_store.get()

    i = 0
    while i < len(store['users']):
        user = store['users'][i]
        if user['handle_str'] == handle_str:
            return False 
        i += 1
    
    pass 

def check_alpha_num(string):
    if string.isalnum() == False:
        return False
    
    pass 

def input_error(error):
    if error == False:    
        return False
 
    pass 

# HELPER FUNCTIONS 
def check_valid_email(email):
    # check whether it is valid email 
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        return False 

    pass

def check_name_length(name):
    if len(name) < 1 or len(name) > 50:
        return False

    pass

def check_password_length(password):
    if len(password) < 6:
        return False
    
    pass

def check_duplicate_email(email):
    store = data_store.get()

    i = 1
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        if user['email'] == email:
            return False 
        i += 1
    
    pass 


# USERS FUNCTIONS
def users_all_v1(token):
    """
    Returns a list of all users and their associated details.
    """
    store = data_store.get()

    token_check(token)
     
    return { 'users': store['users'] } 

def user_profile_v1(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    """

    store = data_store.get()
    
    token_check(token)
    decoded_token = decode_JWT(token)
    
    i = 0
    while i < len(store['users']):
        user = store['users'][i] 
        if user['u_id'] == decoded_token['u_id']:
            return {'user' : user}
        i += 1 

    # if no match 
    raise InputError("Invalid u_id")

def user_profile_setname_v1(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    """
    store = data_store.get()

    if check_name_length(name_first) == False:
        raise InputError

    if check_name_length(name_last) == False:
        raise InputError

    token_check(token)
    decoded_token = decode_JWT(token)

    # update users dict 
    i = 0
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == decoded_token['u_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last
            data_store.set(store)
            return { } 

        i += 1 
    
    # # if user does not exist
    # raise InputError("Invalid user") 

def user_profile_setemail_v1(token, email):
    """
    Update the authorised user's email address 
    """
    store = data_store.get()

    if check_duplicate_email(email) == False:
        raise InputError

    if check_valid_email(email) == False:
        raise InputError
 
    if token_check(token) == False:
        raise AccessError

    decoded_token = decode_JWT(token)
    
    # update users dict 
    i = 0
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == decoded_token['u_id']:
            user['email'] = email
            data_store.set(store)
            return { } 

        i += 1 
    
    # if user does not exist
    raise InputError("Invalid user")

def user_profile_sethandle_v1(token, handle_str):

    store = data_store.get()
    if check_handle(handle_str) == False:
        raise InputError

    if check_duplicate_handle(handle_str) == False:
        raise InputError

    if check_alpha_num(handle_str) == False:
        raise InputError

    if token_check(token) == False:
        raise AccessError

    decoded_token = decode_JWT(token)

    # update users dict 
    i = 0
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == decoded_token['u_id']:
            user['handle_str'] = handle_str
            data_store.set(store)
            return { } 

        i += 1 
    
    # if user does not exist
    raise InputError("Invalid user")
