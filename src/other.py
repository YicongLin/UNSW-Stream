from src.data_store import data_store
from src.error import InputError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.users import token_check
from src.message import valid_message_length
import re

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

def search_v1(token, query_str):
    """Given a query string, returning a collection of messages in all channels/DMs 
       that the authorised user has joined that contain the query.
   
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        query_str (string) - the query string to be found in all messages
       
    Exceptions:
        InputError - Occurs when the length of query_str is less than 1 or over 1000 characters
    
    Return Value:
        Returns 'messages' on all valid conditions
    """

    # obtaining data
    data = data_store.get()
    auth_user_id = decode_JWT(token)['u_id']
    channels = data['channels_details']
    dms = data['dms_details']

    # checks for exceptions
    token_check(token)
    valid_message_length(query_str)

    matched_messages = []

    # finding the channels the authorised user is a member of 
    for i in range(len(channels)):
        channel_members = channels[i]['channel_members']
        for j in range(len(channel_members)):
            # if the user is a member of a channel, apply the search to all messages
            # within the channel and append those with a match
            if channel_members[j]['u_id'] == auth_user_id:
                channel_messages = channels[i]['messages']
                for x in range(len(channel_messages)):
                    # if there is a match with the query string in a message, append the message
                    if re.search(query_str, channel_messages[x]['message']):
                        matched_messages.append(channel_messages[x])
    
    # finding the DMs the authorised user is a member of 
    for i in range(len(dms)):
        dm_members = dms[i]['members']
        for j in range(len(dm_members)):
            # if the user is a member of a DM, apply the search to all messages
            # within the DM and append those with a match 
            if dm_members[j]['u_id'] == auth_user_id:
                dm_messages = dms[i]['messages']
                for x in range(len(dm_messages)):
                    # if there is a match with the query string in a message, append the message
                    if re.search(query_str, dm_messages[x]['message']):
                        matched_messages.append(dm_messages[x])
    
    return {'messages': matched_messages}



   

    
