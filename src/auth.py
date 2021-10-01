from src.data_store import data_store
from src.error import InputError
import re 

def auth_login_v1(email, password): 
    store = data_store.get()
    # check if email is valid 
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        raise InputError("Invalid email")

    # search if email is in datastore 
    for user in store['users']:
        # if email is not registered, raise an error, this is not allowed  
        if user['email'] != email:
            raise InputError('Email is not registered')

        # if registered, see if password matches the email password & then return auth_user_id 
        if user['email'] == email:
            if user['password'] == password:
                return user['user_id']
            elif user['password'] != password:
                raise InputError('Incorrect password')

        

def auth_register_v1(email, password, name_first, name_last):
    store = data_store.get()
    
    # check whether it is valid email 
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        raise InputError("Invalid email")
    
    # check first name length 
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Invalid first name")
    # check last name length 
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Invalid last name")
    # check password length 
    if len(password) < 6:
        raise InputError("Password too short")
    # check duplicate email 
    for user in store['users']:
        if user['email'] == email: 
            raise InputError("Duplicate email")
    
    # auth user id is the number of users + 1 
    new_id = len(store['users']) + 1
    # first create dictionary 
    user_dict = {
        'user_id' : new_id, 
        'email' : email, 
        'password' : password, 
        'first_name' : name_first, 
        'last_name' : name_last
    }
    # add dictionary into the list 'users'
    store['users'].append(user_dict)
     
    data_store.set(store)
    return user_dict['user_id']
