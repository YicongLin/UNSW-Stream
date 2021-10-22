import re 
import json
import jwt
from src.data_store import data_store
from src.error import InputError, AccessError
from src.token_helpers import decode_JWT
from src.auth import check_name_length, check_valid_email, check_duplicate_email

# HELPER FUNCTIONS 
def token_check(token):
    decoded_token = decode_JWT(token)
    store = data_store.get()
    
    found = False 
    i = 1
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        # check if session id matches any current session id’s 
        if decoded_token['session_id'] == user['session_id']:
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

    i = 1
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

    # search through users to find correct user 
    # for user in store['users']:
    #     if u_id == user['u_id']:
    #         return {'user' : user}
    
    i = 1
    while i < len(store['users']):
        user = store['users'][i]
        if u_id == user['u_id']:
            return {'user' : user}

        i += 1 

    # if no match 
    raise InputError("Invalid u_id")
        
def user_profile_setname_v1(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    """
    store = data_store.get()

    check_name_length(name_first)
    check_name_length(name_last)


    token_check(token)

    # for user in store['users']:
    #     if user['u_id'] == token['u_id']:
    #         user['name_first'] = name_first
    #         user['name_last'] = name_last 

    # update users dict 
    i = 1
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == token['u_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last
            data_store.set(store)
            return { } 

        i += 1 
    
    # if user does not exist
    raise InputError("Invalid user") 

def user_profile_setemail_v1(token, email):
    """
    Update the authorised user's email address 
    """
    store = data_store.get()

    check_duplicate_email(email)
    check_valid_email(email)

    token_check(token)
    
    # update users dict 
    i = 1
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == token['u_id']:
            user['email'] = email
            data_store.set(store)
            return { } 

        i += 1 
    
    # if user does not exist
    raise InputError("Invalid user")

def user_profile_sethandle_v1(token, handle_str):

    check_handle(handle_str)
    check_duplicate_handle(handle_str)
    check_alpha_num(handle_str)
    
    store = data_store.get()
    token_check(token)

    # update users dict 
    i = 1
    while i < len(store['users']):
        user = store['users'][i]
        if user['u_id'] == token['u_id']:
            user['handle_str'] = handle_str
            data_store.set(store)
            return { } 

        i += 1 
    
    # if user does not exist
    raise InputError("Invalid user")

    

    

