from src.data_store import data_store
from src.error import InputError, AccessError
import re 
import hashlib
from src.token_helpers import generate_new_session_id, generate_JWT, decode_JWT
from src.users import token_check, check_name_length, check_valid_email, check_duplicate_email, check_password_length

def auth_login_v2(email, password): 
    """The auth_login_v1 function allows users who have registered with emails to login to their 
    account, if they give the correct password.

    Arguments: 
        email (string) - correctly registered user email 
        password (string) - password which corresponds to user email 

    Exceptions:
        InputError - Occurs when the email is not registered, or the incorrect password is entered.
        AccessError - None 

    Return Value: 
        Returns auth_user_id if the correct password is returned for the email
    """

    store = data_store.get()
    check_valid_email(email)

    # search if email is in datastore 
    i = 1
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        if user['email'] == email:
            # if password is not correct, raise error 
            if user['password'] != hashlib.sha256(password.encode()).hexdigest():
                raise InputError('Incorrect password')
            # if password is correct 
            else:    
                u_id = user['u_id']
                permissions_id = store['emailpw'][i]['permissions_id']
        
                # create session id + store into session id list 
                new_session_id = generate_new_session_id()
                # append new session id into list of session id's 
                store['emailpw'][i]['session_id'].append(new_session_id)

                # generate token
                token = generate_JWT(u_id, permissions_id, new_session_id)
                data_store.set(store)

                return { 
                        'token' : token,
                        'auth_user_id': u_id
                    }     
        i += 1      
    
    raise InputError("No matching email")

def auth_register_v2(email, password, name_first, name_last):
    """The auth_register_v1 function takes in a valid email, password, user's first name, and 
    user's last name and registers an account, as well as user handle for the user.

    Arguments: 
        email (string) - correctly registered user email 
        password (string) - password which corresponds to user email 
        name_first (string) - user's first name
        name_last (string) - user's last name

    Exceptions:
        InputError - Occurs when there is invalid first or last name (less than 1-50 characters inclusive), 
        email address is already registered with another user, length of password is less than 6 characters,
        email address is invalid.
        AccessError - None

    Return Value: 
        Returns a new auth_user_id for each user email
    """

    store = data_store.get()
    
    check_valid_email(email)
    check_name_length(name_first)
    check_name_length(name_last)
    check_password_length(password)
    
    if len(store['users']) > 1:
        check_duplicate_email(email)
    
    # auth user id is the number of users + 1 
    new_id = len(store['users']) + 1

    # create new user handle - remove characters that are not letter or numbers 
    # https://thispointer.com/python-remove-all-non-alphanumeric-characters-from-string/
    pattern = r'[^A-Za-z0-9]+'
    lowercase_name = (name_first + name_last).lower()
    user_handle = re.sub(pattern, '', lowercase_name)
   
    # only take 20 characters 
    if len(user_handle) > 20:
        user_handle = user_handle[:20]

    # check if duplicate handle 
    flag = False
    i = 1
    while i < len(store['users']):
        user = store['users'][i]
        if user['handle_str'][:20] == user_handle:
            flag = True  
        i += 1

    # if user handle has been taken, create new 
    if flag == True:
        # if no number yet 
        if len(user['handle_str']) == len(user_handle):
            number = 0
            user_handle = user_handle + str(number)
        # already has number  
        elif len(user['handle_str']) > len(user_handle):
            diff = len(user['handle_str']) - len(user_handle)
            number = int(user['handle_str'][-diff:]) + 1
            user_handle = user_handle + str(number)
            
    # first create user dictionary 
    user = {
        'u_id' : new_id, 
        'email' : email, 
        'name_first' : name_first, 
        'name_last' : name_last,
        'handle_str' : user_handle
    }
    # add user dictionary into the list 'users'
    store['users'].append(user)

    # new session id 
    session_id = generate_new_session_id()

    # check length of user dictionary, first user perm is 1, everyone else is 2
    number_users = len(store['users'])

    if number_users == 1:
        permissions_id = 1
    elif number_users >= 2:
        permissions_id = 2

    # generate token 
    token = generate_JWT(new_id, permissions_id, session_id)

    # create dictionary of emails and passwords and tokens 
    email_password = {
        'email' : email,
        'password' : hashlib.sha256(password.encode()).hexdigest(),
        'u_id' : new_id,
        'permissions_id' : permissions_id,
        'session_id' : [session_id]
    }
    
    # add email+password dictionary into the list 'emailpw'
    store['emailpw'].append(email_password)

    data_store.set(store)
    
    return { 
        'token' : token,
        'auth_user_id': new_id 
        }

def auth_logout_v1(token):
    store = data_store.get()
    token_check(token)

    decoded_token = decode_JWT(token)
    session_id = decoded_token['session_id']

    # remove session_id from user list of session id's
    i = 1
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        # check if session id matches any current session id’s 
        if session_id in user['session_id']:
            # remove session_id
            user['session_id'].remove(session_id)
            data_store.set(store)
            return { }
        
        i += 1 

    raise InputError("Invalid session id")