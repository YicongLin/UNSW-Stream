from src.data_store import data_store
from src.error import InputError
import re 
from src.token_helpers import generate_new_session_id, generate_JWT, decode_JWT

# def auth_login_v1(email, password): 
#     """The auth_login_v1 function allows users who have registered with emails to login to their 
#     account, if they give the correct password.

#     Arguments: 
#         email (string) - correctly registered user email 
#         password (string) - password which corresponds to user email 

#     Exceptions:
#         InputError - Occurs when the email is not registered, or the incorrect password is entered.
#         AccessError - None 

#     Return Value: 
#         Returns auth_user_id if the correct password is returned for the email
#     """

#     store = data_store.get()
#     # check if email is valid 
#     regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     if not (re.fullmatch(regex, email)):
#         raise InputError("Invalid email")

#     # search if email is in datastore 
#     for user in store['emailpw']:
#         # if email is not registered, raise an error, this is not allowed  
#         for i in range(len(store['users'])):
#             if store[i]['email'] != email:
#                 raise InputError('Email is not registered')

#         # if registered, see if password matches the email password & then return auth_user_id    
#         for i in range(len(store['users'])):
#             if store[i]['password'] == password:
#                 return { 'auth_user_id': user['u_id'] }
#             elif store[i]['password'] != password:
#                 raise InputError('Incorrect password')

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
    # check if email is valid 
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        raise InputError("Invalid email")

    # search if email is in datastore 
    email_password = store['emailpw']
    for i in range(len(email_password)):
        if email_password[i]['email'] == email:
            # if password is not correct, raise error 
            if email_password[i]['password'] != password:
                raise InputError('Incorrect password')
            # if password is correct... 
            else:    
                u_id = email_password[i]['u_id']
                permissions_id = email_password[i]['permissions_id']
        
                # create session id + store into session id list 
                new_session_id = generate_new_session_id()
                email_password[i]['session_id'].append(new_session_id)
                # generate token
                token = generate_JWT(u_id, permissions_id, new_session_id)
        else:
            raise InputError("Invalid email")

    # element = 0
    # while element < len(email_password):
    #     if email_password[element]['email'] == email:
    #         # if password is not correct, raise error 
    #         if email_password[element]['password'] != password:
    #             raise InputError('Incorrect password')
    #         # if password is correct... 
    #         else:    
    #             u_id = email_password[element]['u_id']
    #             permissions_id = email_password[element]['permissions_id']
        
    #             # create session id + store into session id list 
    #             new_session_id = generate_new_session_id()
    #             email_password[element]['session_id'].append(new_session_id)
    #             # generate token
    #             token = generate_JWT(u_id, permissions_id, new_session_id)

    #     # else there is no matching email 
    #     else:
    #         raise InputError("Invalid email")
            
    #     element += 1
    
    data_store.set(store)

    return { 
            'token' : token,
            'auth_user_id': u_id
        }

    # for user in store['emailpw']:
    #     # if email is not registered, raise an error, this is not allowed 
    #     found = False 
    #     for i in range(len(store['users'])):
    #         if store[i]['email'] == email:
    #             found = True
        
    #     if found == False:
    #         raise InputError("Invalid email")

    #     # # if registered, see if password matches the email password & then return auth_user_id    
    #     # for i in range(len(store['users'])):
    #     #     if store[i]['password'] == password:
    #     #         return { 'auth_user_id': user['u_id'] }
    #     #     elif store[i]['password'] != password:
    #     #         raise InputError('Incorrect password')
        
    #     # if registered, input error if password doesn't match 
    #     for i in range(len(store['users'])):
    #         if store[i]['email'] == email and store[i]['password'] != password:
    #             raise InputError('Incorrect password')

    #     # if registered and correct password
    #     for i in range(len(store['emailpw'])):
    #         if store[i]['email'] == email and store[i]['password'] == password:
    #             u_id = store[i]['u_id']
    #             permissions_id = store[i]['permissions_id']
        
    #             # create session id + store into session id list 
    #             new_session_id = generate_new_session_id()
    #             store['email_password']['session_id'].append(new_session_id)



    #     # check if password matches email 
    #         if store[i]['password'] == password:
    #             token = generate_JWT(u_id, permissions_id, session_id)

    #         return { 
    #             'token' : token,
    #             'auth_user_id': 
    #         }
        
        
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

# def check_duplicate_email(email):
#     store = data_store.get()
#     for i in range(len(store['users'])):
#         if store[i]['email'] == email:
#             return False 
    
#     pass 

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
    
    # if len(store['users']) > 0:
    #     check_duplicate_email(email)
    
    # auth user id is the number of users + 1 
    new_id = len(store['users']) + 1

    # create new user handle - remove characters that are not letter or numbers 
    # https://thispointer.com/python-remove-all-non-alphanumeric-characters-from-string/
    pattern = r'[^A-Za-z0-9]+'
    lowercase_name = ('name_first' + 'name_last').lower()
    user_handle = re.sub(pattern, '', lowercase_name)
   
    # only take 20 characters 
    user_handle = user_handle[:20]

    # if len(store['users']) > 0:
    #     # search if user handle has already been taken 
    #     for user in store['users']:
    #         # if handle has been taken  
    #         if (user['handle_str'])[:20] == user_handle:
    #             # create new handle using next 
    #             if len(user['handle_str']) == 20:
    #                 number = 0
    #             elif len(user['handle_str']) >= 21:
    #                 number = int(user['handle_str'][20:]) + 1
    #             user_handle = 'user_handle' + str(number)
            

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

    if number_users == 0:
        permissions_id = 1
    elif number_users >= 1:
        permissions_id = 2

    # generate token 
    token = generate_JWT(new_id, permissions_id, session_id)

    # create dictionary of emails and passwords and tokens 
    email_password = {
        'email' : email,
        'password' : password,
        'u_id' : new_id,
        'permissions_id' : permissions_id,
        'session_id' : [session_id]
    }
    
    # add email+password dictionary into the list 'users'
    store['emailpw'].append(email_password)

    data_store.set(store)
    
    return { 
        'token' : token,
        'auth_user_id': new_id 
        }


