from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from datetime import datetime, timezone
from src.users import token_check
from src.channel import check_channel, not_a_member
import hashlib
import jwt
from src.token_helpers import decode_JWT
import math

# ================================================
# ================== HELPERS =====================
# ================================================

# Raises an error if the dm_id is invalid
def valid_dm_id(dm_id):
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']

    # looping through data store to create a list of valid dm_ids
    dm_ids_list = []
    for i in range(len(dm_details)):
        dm_ids_list.append(dm_details[i]['dm_id'])

    # raising the error
    if int(dm_id) not in dm_ids_list:
        raise InputError(description="Invalid DM")

# Raises an error if the message length is less than 1 or greater than 1000 characters
def valid_message_length(message):
    if len(message) < 1 or len(message) > 1000:
        raise InputError("Invalid message length")

def valid_message_length_edit(message):
    if len(message) > 1000:
        raise InputError("Invalid message length")

# Raises an error if the authorised user is not a member of the DM
def check_dm_member(token, dm_id):
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    dm_details = data['dms_details']

    # creating a list of members within the given DM
    dm_members_list = []
    for i in range(len(dm_details)):
        if dm_details[i]['dm_id'] == int(dm_id):
            dm_members = dm_details[i]['members']
            for j in range(len(dm_members)):
                dm_members_list.append(dm_members[j]['u_id'])
    
    # raising the error
    if auth_user_id not in dm_members_list:
        raise AccessError("Not a member of the DM")

# Obtain and return channel/dm ID that the message is in, along with relevant information
def return_info(message_id):
    # obtaining data
    data = data_store.get()
    channels = data['channels_details']
    dms = data['dms_details']

    # if the message is in a channel, finding the channel 
    # and returning the channel ID, 'channel' type, and the ID of the user that sent the message
    for i in range(len(channels)):
        channel_messages = channels[i]['messages']
        for j in range(len(channel_messages)):
            if channel_messages[j]['message_id'] == int(message_id):
                return channels[i]['channel_id'], 'channel', channel_messages[j]['u_id']

    # if the message is in a DM, finding the DM 
    # and returning the DM ID, 'dm' type, and the ID of the user that sent the message
    for i in range(len(dms)):
        dm_messages = dms[i]['messages']
        for j in range(len(dm_messages)):
            if int(dm_messages[j]['message_id']) == int(message_id):
                return dms[i]['dm_id'], 'dm', dm_messages[j]['u_id']

# Raises an error if the message_id is invalid in the channel/DM that the authorised user has joined
def valid_message_id(token, message_id):
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    channels = data['channels_details']
    dms = data['dms_details']

    # looping through all channels to determine which ones the authorised user is a member of
    valid = False
    for i in range(len(channels)):
        channel_members = channels[i]['channel_members']
        for j in range(len(channel_members)):
            if channel_members[j]['u_id'] == auth_user_id:
                channel_messages = channels[i]['messages']
                # looping through the messages in the channel to find a match for the message_id
                for j in range(len(channel_messages)):
                    # the message_id is valid if there is a match
                    if channel_messages[j]['message_id'] == int(message_id):
                        valid = True

    # looping through all DMs to determine which ones the authorised user is a member of
    for i in range(len(dms)):
        dm_members = dms[i]['members']
        for j in range(len(dm_members)):
            if dm_members[j]['u_id'] == auth_user_id:
                dm_messages = dms[i]['messages']
                # looping through the messages in the DM to find a match for the message_id
                for j in range(len(dm_messages)):
                    # the message_id is valid if there is a match
                    if dm_messages[j]['message_id'] == int(message_id):
                        valid = True
    
    # raising the error if there is no match
    if valid == False:
        raise InputError("Invalid message ID")

# Returning false if the authorised user doesn't have owner permissions 
# in the channel/DM that a given message is in
def owner_permissions(token, message_id):
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    channels = data['channels_details']
    dms = data['dms_details']

    # determining what channel/DM the message is in and obtaining information
    a, b, _ = return_info(message_id)

    # if the message is in a channel, creating a list of channel owner members
    owner_members_list = []
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == int(a):
                owner_members = channels[i]['owner_members']
                for j in range(len(owner_members)):
                    owner_members_list.append(owner_members[j]['u_id'])
        if auth_user_id not in owner_members_list:
            return False

    # if the message is in a DM, determing whether the authorised user is the creator of the DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == int(a):
                creator = dms[i]['creator']
                if creator[0]['u_id'] != auth_user_id:
                    return False

# Raises an error if none of the following conditions are true:
# - the message was sent by the authorised user
# - the authorised user has owner permisisons in the channel/DM
def conditional_edit(token, message_id):
    # obtaining data
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # determining what channel/DM the message is in and obtaining information
    _, _, c = return_info(message_id)

    # raising the error 
    if int(c) != auth_user_id and owner_permissions(token, message_id) == False:
        raise AccessError(description="You do not have access to edit the message")

# ================================================
# ================= FUNCTIONS ====================
# ================================================

def message_senddm_v1(token, dm_id, message):
    """Send a message from the authorised user to the specified DM.
   
    Arguments:
        token (string) - the token of a authorised user
        dm_id (integer) - the ID of an existing DM
        message (string) - message to be sent
       
    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid DM
        InputError - Occurs when the message length is invalid
        AccessError - Occurs when the authorised user is not a member of the valid DM
    
    Return Value:
        Returns message_id on all valid conditions
    """
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    # checks for exceptions
    token_check(token)    
    valid_dm_id(dm_id) 
    valid_message_length(message)
    check_dm_member(token, dm_id)
    
    # otherwise, send the message to the specified DM

    # obtain the total number of messages existing in order to assign a message ID
    length_of_messages = 0
    for i in range(len(dm_details)):
        length_of_messages += len(dm_details[i]['messages'])
    for i in range(len(channel_details)):
        length_of_messages += len(channel_details[i]['messages'])
 
    # assigning the message ID
    message_id = length_of_messages + 1

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created,
    }

    # finding the DM with given dm_id and appending the message to the DM's details
    for i in range(len(dm_details)):
        if dm_details[i]['dm_id'] == int(dm_id):
            data['dms_details'][i]['messages'].append(message_dict)
            data_store.set(data)

    return {"message_id": message_id}

def message_send_v1(token, channel_id, message):
    """
     Send a message from the authorised user to the specified channel.
   
    Arguments:
        token (string) - the token of a authorised user
        channel_id (integer) - the ID of an existing channel
        message (string) - message to be sent
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the message length is invalid
        AccessError - Occurs when the authorised user is not a member of the valid channel
    
    Return Value:
        Returns message_id on all valid conditions
    """
 
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    # checks for exceptions
    token_check(token)    
    check_channel(channel_id)
    valid_message_length(message)
    not_a_member(auth_user_id, channel_id)
    
    # otherwise, send the message to the specified channel

    # obtain the total number of messages existing in order to assign a message ID
    length_of_messages = 0
    for i in range(len(dm_details)):
        length_of_messages += len(dm_details[i]['messages'])
    for i in range(len(channel_details)):
        length_of_messages += len(channel_details[i]['messages'])
 
    # assigning the message ID
    message_id = length_of_messages + 1

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created
    }

    # finding the channel with given channel_id and appending the message to the DM's details
    for i in range(len(channel_details)):
        if int(channel_details[i]['channel_id']) == int(channel_id):
            data['channels_details'][i]['messages'].append(message_dict)
            data_store.set(data)
    
    return {"message_id": message_id}

def message_edit_v1(token, message_id, message):
    """
    Given a message, update its text with new text.

    Arguments:
        token (string) - the token of a authorised user
        message_id (integer) - the ID of a message
        message (string) - message to be sent

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - length of message is less than 1 or over 1000 characters
        AccessError - when message_id refers to a valid message in a joined channel/DM
                    where the message was sent by the authorised user and the user has owner permissions

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    # checks for exceptions
    valid_message_length_edit(message)
    valid_message_id(token, message_id)
    conditional_edit(token, message_id)
    
    # obtaining what channel/DM the message is in 
    a, b, _ = return_info(message_id)
    print('edit:')
    print(b)

    # if the message is in a DM, access the DM the message is in, in order to edit the message
    index = False
    if b == 'dm':
        for i in range(len(dm_details)):
            if dm_details[i]['dm_id'] == int(a):
                dm_messages = dm_details[i]['messages']
                for j in range(len(dm_messages)):
                    # find the message
                    if dm_messages[j]['message_id'] == int(message_id):
                        # if the new message is an empty string, delete the message
                        if message == "":
                            message_index = j
                            index = True
                        # otherwise, replace the message with the new text
                        else:
                            dm_messages[j]['message'] = message
                            data_store.set(data)
                if index == True:
                    del dm_messages[message_index]
                    data_store.set(data)

    # if the message is in a channel, access the channel the message is in, in order to edit the message
    else:
        index = False 
        for i in range(len(channel_details)):
            if channel_details[i]['channel_id'] == int(a):
                channel_messages = channel_details[i]['messages']
                for j in range(len(channel_messages)):
                    # find the message
                    if channel_messages[j]['message_id'] == int(message_id):
                        # if the new message is an empty string, delete the message
                        if message == "":
                            index = True
                            message_index = j
                        # otherwise, replace the message with the new text
                        else:
                            channel_messages[j]['message'] = message
                            data_store.set(data)
                if index == True:
                    del channel_messages[message_index]
                    data_store.set(data)

    return {}

# function for removing messages
def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
            token (string) - the token of a authorised user
            message_id (integer) - the ID of a message

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - length of message is less than 1 or over 1000 characters
        AccessError - when message_id refers to a valid message in a joined channel/DM
                    where the message was sent by the authorised user and the user has owner permissions

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    # checks for exceptions
    valid_message_id(token, message_id)
    conditional_edit(token, message_id)
    
    # obtaining what channel/DM the message is in 
    a, b, _ = return_info(message_id)

    # if the message is in a DM, access the DM the message is in, in order to remove the message
    index = False
    if b == 'dm':
        for i in range(len(dm_details)):
            if int(dm_details[i]['dm_id']) == int(a):
                dm_messages = dm_details[i]['messages']
                for j in range(len(dm_messages)):
                    # find the message
                    if dm_messages[j]['message_id'] == int(message_id):
                        message_index = j
                        index = True
                if index == True:
                    del dm_messages[message_index]
                    data_store.set(data)

    # if the message is in a channel, access the channel the message is in, in order to remove the message
    else:
        index = False
        for i in range(len(channel_details)):
            if channel_details[i]['channel_id'] == int(a):
                channel_messages = channel_details[i]['messages']
                for j in range(len(channel_messages)):
                    # find the message
                    if channel_messages[j]['message_id'] == int(message_id):
                        message_index = j
                        index = True
                if index == True:
                    del channel_messages[message_index]
                    data_store.set(data)
    return {}

def message_react_v1(token, message_id, react_id ):
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']
    is_this_user_reacted 
    return {}

def message_unreact_v1(token, message_id, react_id ):
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    return {}

def message_pin_v1(token, message_id):
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']
    is_pinned

    return {}

def message_unpin_v1(token, message_id):
    # obtaining data
    data = data_store.get()
    dm_details = data['dms_details']
    channel_details = data['channels_details']

    return {}
    