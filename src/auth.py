from src.data_store import data_store
from src.error import InputError
import re 

def auth_login_v1(email, password): 
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
    for user in store['emailpw']:
        # if email is not registered, raise an error, this is not allowed  
        if user['email'] != email:
            raise InputError('Email is not registered')

        # if registered, see if password matches the email password & then return auth_user_id 
        if user['email'] == email:
            if user['password'] == password:
                return user['u_id']
            elif user['password'] != password:
                raise InputError('Incorrect password')
        
def auth_register_v1(email, password, name_first, name_last):
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

    # create new user handle - remove characters that are not letter or numbers 
    # https://thispointer.com/python-remove-all-non-alphanumeric-characters-from-string/
    pattern = r'[^A-Za-z0-9]+'
    lowercase_name = ('name_first' + 'name_last').lower()
    user_handle = re.sub(pattern, '', lowercase_name)
   
    # only take 20 characters 
    user_handle = user_handle[:20]

    # search if user handle has already been taken 
    for user in store['users']:
        # if handle has been taken  
        if (user['handle_str'])[:20] == user_handle:
            # create new handle using next 
            if len(user['handle_str']) == 20:
                number = 0
            elif len(user['handle_str']) == 21:
                number = int(user['handle_str'][20]) + 1
            user_handle = 'user_handle' + 'number'
            
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

    # create dictionary of emails and passwords 
    email_password = {
        'email' : email,
        'password' : password,
        'u_id' : new_id
    }
    
    # add email+password dictionary into the list 'users'
    store['emailpw'].append(email_password)
     
    data_store.set(store)
    return user['u_id']
