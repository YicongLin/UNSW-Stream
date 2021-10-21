import re 
from data_store import data_store
from error import InputError

def users_all_v1(token):
    """
    Returns a list of all users and their associated details.
    """
    store = data_store.get()
    return { 'users': store['users'] } 

def user_profile_v1(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    """

    store = data_store.get()
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

    store = data_store.get()
    # input error if length of name_first is not between 1 and 50 characters inclusive
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Invalid first name")
    
    # input error if length of name_last is not between 1 and 50 characters inclusive
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Invalid last name")

    # search through users to find correct user 
    for user in store['users']:  
        # if token == 
            user['name_first'] = name_first
            user['name_last'] = name_last
    
    # check if user exists 

    data_store.set(store)
    return { }

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

    # search through users to find correct user 
    for user in store['users']:  
        # if token == 
            user['email'] = email

    data_store.set(store)
    return { }

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

    # search through users to find correct user 
    for user in store['users']:  
        # if token == 
            user['handle_str'] = handle_str
    
    data_store.set(store)
    return { }

