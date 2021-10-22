import re 
import json
import jwt
from src.data_store import data_store
from src.error import InputError, AccessError
from src.token_helpers import decode_JWT

def users_all_v1(token):
    """
    Returns a list of all users and their associated details.
    """
    store = data_store.get()

    # decode the token and check session id 
    decoded_token = decode_JWT(token)

    found = False 
    for user in store['emailpw']:
		# check if session id matches any current session id’s 
	    if decoded_token['session_id'] == user['session_id']:
		    found = True 

    if found == False:
        raise AccessError("Invalid token") 
    elif found == True: 
	    return { 'users': store['users'] } 

def user_profile_v1(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    """

    store = data_store.get()
    
    # decode the token and check session id 
    decoded_token = decode_JWT(token)

    found = False 
    for user in store['emailpw']:
		# check if session id matches any current session id’s 
	    if decoded_token['session_id'] == user['session_id']:
		    found = True 

    if found == False:
        raise AccessError("Invalid token")

    # search through users to find correct user 
    for user in store['users']:
        if u_id == user['u_id']:
            return {'user' : user}

    # if no match 
    raise InputError("Invalid u_id")
        
def user_profile_setname_v1(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    """
    # input error if length of name_first is not between 1 and 50 characters inclusive
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Invalid first name")
    
    # input error if length of name_last is not between 1 and 50 characters inclusive
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Invalid last name")

    store = data_store.get()

    # decode the token and check session id 
    decoded_token = decode_JWT(token)

    found = False 
    for user in store['emailpw']:
		# check if session id matches any current session id’s 
	    if decoded_token['session_id'] == user['session_id']:
            found = True 
            current = decoded_token['u_id']

    if found == False:
        raise AccessError("Invalid token")
    
    for user in store['users']:
        if user['u_id'] == current:
            user['name_first'] = name_first
            user['name_last'] = name_last 
 
        data_store.set(store)
        return { }
    
    # if user does not exist 
    raise InputError("Invalid user") 

def user_profile_setemail_v1(token, email):
    """
    Update the authorised user's email address 
    """

    store = data_store.get()
    # input error if invalid email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        raise InputError("Invalid email")    
    
    # input error if duplicate email 
    for user in store['users']:
        if user['email'] == email: 
            raise InputError("Duplicate email")

    # decode the token and check session id 
    decoded_token = decode_JWT(token)

    found = False 
    for user in store['emailpw']:
		# check if session id matches any current session id’s 
	    if decoded_token['session_id'] == user['session_id']:
            found = True
            current = decoded_token['u_id']    

    if found == False:
        raise AccessError("Invalid token")
    
    for user in store['users']:
        if user['u_id'] == current:
            user['email'] = email
 
        data_store.set(store)
        return { }
    
    # if user does not exist 
    raise InputError("Invalid email")

def user_profile_sethandle_v1(token, handle_str):
    store = data_store.get()

    # input error if duplicate handle 
    for user in store['users']:
        if user['handle_str'] == handle_str: 
            raise InputError("Duplicate handle")

    # input error if characters are not all alphanumeric 
    if handle_str.isalnum() == False:
        raise InputError("Not all alphanumeric")

    # input error if length of handle_str is not between 3 and 20 characters inclusive
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Handle must be between 3 and 20 characters inclusive")
    
    # decode the token and check session id 
    decoded_token = decode_JWT(token)

    found = False 
    for user in store['emailpw']:
		# check if session id matches any current session id’s 
	    if decoded_token['session_id'] == user['session_id']:
            found = True
            current = decoded_token['u_id']    

    if found == False:
        raise AccessError("Invalid token")
    
    for user in store['users']:
        if user['u_id'] == current:
            user['handle_str'] = handle_str
 
        data_store.set(store)
        return { }
    
    # if handle does not exist 
    raise InputError("Invalid handle_str")

    

