import re 
import json
import jwt
from werkzeug.exceptions import RequestedRangeNotSatisfiable
from src.data_store import data_store
from src.error import InputError, AccessError
from src.token_helpers import decode_JWT
import urllib.request
from urllib.error import HTTPError, URLError
from PIL import Image
from src.config import url

# HELPER FUNCTIONS 
def token_check(token):
    store = data_store.get()
    decoded_token = decode_JWT(token)
    
    i = 0
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        # check if session id matches any current session id’s 
        if decoded_token['session_id'] in user['session_id']:
            return 

        i += 1 

    raise AccessError(description = 'token_check: Invalid token')

def u_id_check(u_id):
    store = data_store.get()
    
    users_length = len(store['users'])

    found = False 
    i = 0
    while i < users_length:
        user = store['users'][i]
        # check if uid matches any uid
        if int(user["u_id"]) == int(u_id):
            found = True

        i += 1 
    deleted_users = store['deleted_users']
    for i in range(len(deleted_users)):
        if int(deleted_users[i]['u_id']) == int(u_id):
            found = True
    
    if found == False:
        raise InputError(description = 'u_id_check: Invalid u_id')

def check_handle(handle_str):
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description = 'check_handle: Invalid handle_str')
     
    return

def check_duplicate_handle(handle_str):
    store = data_store.get()

    i = 0
    while i < len(store['users']):
        user = store['users'][i]
        if user['handle_str'] == handle_str:
            raise InputError(description = 'check_duplicate_handle: Duplicate handle') 
        i += 1
    
    return 

def check_alpha_num(string):
    if string.isalnum() == False:
        raise InputError(description = 'check_alpha_num: Handle_str not all alphanumeric')  
    
    return

# HELPER FUNCTIONS 
def check_valid_email(email):
    # check whether it is valid email 
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        raise InputError(description = 'check_valid_email: Invalid email') 
    
    return 

def check_name_length(name):
    if len(name) < 1 or len(name) > 50:
        raise InputError(description = 'check_name_length: Invalid name length') 

    return 

def check_password_length(password):
    if len(password) < 6:
        raise InputError(description = 'check_password_length: Password too short') 
    
    return 

def check_duplicate_email(email):
    store = data_store.get()

    i = 0
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        if user['email'] == email:
            raise InputError(description = 'check_duplicate_email: Duplicate email') 
        i += 1
    
    return  

# ==================================
# Return the index about where uid stroes in users list
# Associate with other uploadphoto functions
def users_index(auth_user_id):

    data = data_store.get()

    users_index = 0
    while True:
        if data['users'][users_index]['u_id'] == auth_user_id:
            break
        users_index += 1

    data_store.set(data)

    return users_index 
# Finish function
# ==================================

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
    u_id_check(u_id)

    i = 0
    while i < len(store['users']):
        user = store['users'][i] 
        if int(user['u_id']) == int(u_id):
            return {'user' : user}
        i += 1 

    i = 0
    while i < len(store['deleted_users']):
        user = store['deleted_users'][i] 
        if (user['u_id'] == int(u_id)):
            return {'user' : user}
        i += 1 

def user_profile_setname_v1(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    """
    store = data_store.get()

    token_check(token)
    check_name_length(name_first)
    check_name_length(name_last)

    decoded_token = decode_JWT(token)

    # update users dict 
    i = 0
    while True:
        if i < len(store['users']):
            user = store['users'][i]
            if user['u_id'] == decoded_token['u_id']:
                user['name_first'] = name_first
                user['name_last'] = name_last
                data_store.set(store)
                return { } 

            i += 1 
    
def user_profile_setemail_v1(token, email):
    """
    Update the authorised user's email address 
    """
    store = data_store.get()

    token_check(token)
    check_duplicate_email(email)
    check_valid_email(email)

    decoded_token = decode_JWT(token)

    # update users dict 
    i = 0
    while True:
        if i < len(store['users']):
            user = store['users'][i]
            if user['u_id'] == decoded_token['u_id']:
                user['email'] = email
                data_store.set(store)
                return { } 

            i += 1 

def user_profile_sethandle_v1(token, handle_str):

    store = data_store.get()
    token_check(token)
    check_handle(handle_str)
    check_duplicate_handle(handle_str)
    check_alpha_num(handle_str)

    decoded_token = decode_JWT(token)

    # update users dict 
    i = 0
    while True:
        if i < len(store['users']):
            user = store['users'][i]
            if user['u_id'] == decoded_token['u_id']:
                user['handle_str'] = handle_str
                data_store.set(store)
                return { } 
            i += 1 



def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """An authorised user to upload photo(for showing in different secetions)
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        img_url (string) - the url of the photo that authorised user wanna upload
        x_start (integer) - width crop start bound
        y_start (integer) - width crop end bound
        x_end (integer) - height crop start bound
        y_end (integer) - height crop end bound

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        InputError - Occurs when authorised user type in an img_url which causes HTTPErros
        InputError - Occurs when authorised user type in any crop bound out dimensions of the image at the URL
        InputError - Occurs when authorised user type in any start crop bound is less than end bound
        InputError - Occurs when authorised user upload a image is not with jpg or jpeg format

    Return Value:
        {}
    """

    # Obtain data already existed
    data = data_store.get()
    
    # Raise an AccessError if authorised user login with an invalid token
    token_check(token)

    auth_user_id = decode_JWT(token)['u_id']

    # Raise an InputError if authorised user pass in unavailable image url
    try:
        # Get and store the image user upload
        urllib.request.urlretrieve(img_url, f"src/static/{auth_user_id}_temp.jpg")
        img = Image.open(f"src/static/{auth_user_id}_temp.jpg")

        # Raise an InputError if authorised user pass in not JPG image
        if img.format != "JPG" and img.format != "JPEG":
            raise InputError(description="Unacceptable image format")

        # Obtain the size of image
        width, height = img.size

        # Raise an InputError if authorised user type in a bound out of dimensions of the image
        if x_start not in range (0, width + 1) or x_end not in range (0, width + 1):
            raise InputError(description="Out of dimensions of the image")

        if y_start not in range (0, height + 1) or y_end not in range (0, height + 1):
            raise InputError(description="Out of dimensions of the image")

        # Raise an InputError if authorised user type in a impossiable crop bound 
        if x_end < x_start or y_end < y_start:
            raise InputError(description="Impossible crop image bounds")

        # Crop image and save it
        cropped = img.crop((x_start, y_start, x_end, y_end))
        cropped.save(f"src/static/{auth_user_id}.jpg")

        # Obtain index of authorised user's user dict store in users list
        # Update image url to authorised user's user dict
        user_index = users_index(auth_user_id)
        data['users'][user_index]['profile_img_url'] = f'{url}static/{auth_user_id}.jpg'

    except (HTTPError, URLError):
        # if urllib.request.urlopen(img_url).status != 200 or urllib.request.urlretrieve.status != 200:
        raise InputError(description="Unavailable image url") from None

    return {}

