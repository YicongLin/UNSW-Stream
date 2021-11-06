from src.data_store import data_store
from src.error import InputError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.users import token_check

def clear_v1():
    """The function clear_v1 resets all the internal data in data_store.py to its initial state.
    There are no paramaters, no exceptions and no returns.
    """
    store = data_store.get()

    store['users'] = []
    store['channels'] = []
    store['channels_details'] = []
    store['emailpw'] = []
    store['dms_details'] = []
    store['deleted_users'] = []
    store['notifications_details'] = []
    store['removed_messages'] = []

    data_store.set(store)
    
    return {}

def notifications_get_v1(token):
    """Returning an authorised user's most recent 20 notifications, from most recent to least.
   
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
       
    Exceptions:
        None
    
    Return Value:
        Returns 'notifications' on all valid conditions
    """
    # obtaining data
    data = data_store.get()
    notifications_details = data['notifications_details']
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # check for valid token
    token_check(token)

    # return the user's most recent notifications
    notification_list = []
    for i in range(len(notifications_details)):
        if notifications_details[i]['u_id'] == auth_user_id:
            notifications = notifications_details[i]['notifications']
            for j in range(len(notifications)):
                notification_list.append(notifications[j])
    notification_list.reverse()
    return {'notifications': notification_list[:20]}


   

    
