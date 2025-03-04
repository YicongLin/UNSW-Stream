from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from datetime import datetime, timezone
from src.users import token_check
import hashlib
import jwt
from src.token_helpers import decode_JWT
import math
import re

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

# Raises an error if the message length is greater than 1000 characters
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
    # and returning the channel ID, 'channel' type, the ID of the user that sent the message
    # and the message contents
    for i in range(len(channels)):
        channel_messages = channels[i]['messages']
        for j in range(len(channel_messages)):
            if channel_messages[j]['message_id'] == int(message_id):
                return channels[i]['channel_id'], 'channel', channel_messages[j]['u_id'], channel_messages[j]['message']

    # if the message is in a DM, finding the DM 
    # and returning the DM ID, 'dm' type, the ID of the user that sent the message
    # and the message contents
    for i in range(len(dms)):
        dm_messages = dms[i]['messages']
        for j in range(len(dm_messages)):
            if int(dm_messages[j]['message_id']) == int(message_id):
                return dms[i]['dm_id'], 'dm', dm_messages[j]['u_id'], dm_messages[j]['message']

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
# in the channel/DM a given message is in and is not a global owner
def owner_permissions(token, message_id):
    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    channels = data['channels_details']
    dms = data['dms_details']

    # determining what channel/DM the message is in and obtaining information
    a, b, *_ = return_info(message_id)

    # if the message is in a channel, creating a list of channel owner members
    owner_members_list = []
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == int(a):
                owner_members = channels[i]['owner_members']
                for j in range(len(owner_members)):
                    owner_members_list.append(owner_members[j]['u_id'])
        if decoded_token['u_id'] not in owner_members_list and decoded_token['permissions_id'] != 1:
            return False

    # if the message is in a DM, determing whether the authorised user is the creator of the DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == int(a):
                creator = dms[i]['creator']
                if creator[0]['u_id'] != decoded_token['u_id']:
                    return False

# Raises an error if none of the following conditions are true for message_edit:
# - the message was sent by the authorised user
# - the authorised user has owner permisisons in the channel/DM
def conditional_edit(token, message_id):
    # obtaining data
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # determining what channel/DM the message is in and obtaining information
    _, _, c, _ = return_info(message_id)

    # raising the error 
    if int(c) != auth_user_id and owner_permissions(token, message_id) == False:
        raise AccessError(description="You do not have access to edit the message")

# Raises an error if none of the following conditions are true for message_remove:
# - the message was sent by the authorised user
# - the authorised user has owner permisisons in the channel/DM
def conditional_remove(token, message_id):
    # obtaining data
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # determining what channel/DM the message is in and obtaining information
    _, _, c, _ = return_info(message_id)

    # raising the error 
    if int(c) != auth_user_id and owner_permissions(token, message_id) == False:
        raise AccessError(description="You do not have access to remove the message")

# If a message is edited in a DM to include any valid tags, create a notification
def edit_with_tags_check_dm(old_message, new_message, name, dm_id, token):
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []
    
    for i in range(len(new_message)):
        if new_message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', new_message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check that the handle belongs to a valid user in the DM
                if handle_check_dm(handle, dm_id) != None:
                    # if the tag wasn't in the original message, add the notification
                    if not re.search(handle, old_message):
                        # creating a notification dictionary for the user
                        notification_dict = {
                            'channel_id': -1,
                            'dm_id': dm_id,
                            'notification_message': f'{auth_user_handle} tagged you in {name}: {new_message[:20]}'
                        }
                        # adding the notification
                        add_notification(notification_dict, handle_check_dm(handle, dm_id))
                        handle_list.append(handle)

# If a message is edited in a channel to include any valid tags, create a notification
def edit_with_tags_check_channel(old_message, new_message, name, channel_id, token):
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []

    for i in range(len(new_message)):
        if new_message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', new_message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check that the handle belongs to a valid user in the given channel
                if handle_check_channel(handle, channel_id) != None:
                    # if the tag wasn't in the original message, add the notification
                    if not re.search(handle, old_message):
                        # creating a notification dictionary for the user
                        notification_dict = {
                            'channel_id': channel_id,
                            'dm_id': -1,
                            'notification_message': f'{auth_user_handle} tagged you in {name}: {new_message[:20]}'
                        }
                        # adding the notification
                        add_notification(notification_dict, handle_check_channel(handle, channel_id))
                        handle_list.append(handle)

# Returns the number of total messages sent
def number_of_messages():
    # obtaining data
    data = data_store.get()
    channel_details = data['channels_details']
    dm_details = data['dms_details']

    # finding the total number of messages sent
    number_of_messages = 0
    for i in range(len(dm_details)):
        number_of_messages += len(dm_details[i]['messages'])
    for i in range(len(channel_details)):
        number_of_messages += len(channel_details[i]['messages'])
    return number_of_messages

# Determines if a handle belongs to a valid user in a given channel, 
# and returns the u_id of the user if valid
def handle_check_channel(handle, channel_id):
    # obtaining data
    data = data_store.get()
    channels = data['channels_details']
    
    # finding the given channel and its details
    for i in range(len(channels)):
        if channels[i]['channel_id'] == channel_id:
            channel_members = channels[i]['channel_members']
            for j in range(len(channel_members)):
                if channel_members[j]['handle_str'] == handle:
                    return channel_members[j]['u_id']
    return None

# Determines if a handle belongs to a valid user in a given DM, 
# and returns the u_id of the user if valid
def handle_check_dm(handle, dm_id):
    # obtaining data
    data = data_store.get()
    dms = data['dms_details']
    
    # finding the given DM and its details
    for i in range(len(dms)):
        if dms[i]['dm_id'] == dm_id:
            dm_members = dms[i]['members']
            for j in range(len(dm_members)):
                if dm_members[j]['handle_str'] == handle:
                    return dm_members[j]['u_id']
    return None

# Adds a notification for a given user
def add_notification(notification_dict, u_id):
    # obtaining data
    data = data_store.get()
    notifications_details = data['notifications_details']
    
    # add notification
    appended = False

    for i in range(len(notifications_details)):
        # if the user already exists in the notification data store, append relevant information
        if notifications_details[i]['u_id'] == u_id:
            notifications_details[i]['notifications'].append(notification_dict)
            appended = True

    # if the user doesn't already exist, create a new dictionary
    if appended == False:
        notifications = {
            'u_id': u_id,
            'notifications': [notification_dict]
        }
        notifications_details.append(notifications)
    data_store.set(data)

# Finds and returns a user's handle 
def find_handle(token):
    # obtaining data
    data = data_store.get()
    users = data['users']
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    for i in range(len(users)):
        if users[i]['u_id'] == auth_user_id:
            return users[i]['handle_str']

# Raising an error if channel_id is invalid
def check_channel(channel_id):
    data = data_store.get()
    channels = data["channels_details"]
    channel_id_list = []
    for i in range(len(channels)):
        channel_id_list.append(channels[i]['channel_id'])
    if int(channel_id) not in channel_id_list:
        raise InputError(description="Invalid channel")
    
# Raising an error if a user is not a member of the channel
def not_a_member(u_id, channel_id):
    data = data_store.get()
    channels = data["channels_details"]
    is_member = False
    for i in range(len(channels)):
        if int(channels[i]['channel_id']) == int(channel_id):
            members = channels[i]['channel_members']
            for j in range(len(members)):
                if int(members[j]['u_id']) == int(u_id):
                    is_member = True
    if is_member == False:
        raise AccessError("You are not a member of the channel")
        
# Raising an error if both channel_id and dm_id are invalid
def check_valid_channel_and_dm_id(channel_id, dm_id):
    data = data_store.get()
    channels = data["channels_details"]
    dms = data["dms_details"]
    channel_id_list = []
    dm_id_list = []
    valid_channel = True
    valid_dm = True
    for i in range(len(channels)):
        channel_id_list.append(channels[i]['channel_id'])
    if int(channel_id) not in channel_id_list:
        valid_channel = False
    for i in range(len(dms)):
        dm_id_list.append(dms[i]['dm_id'])
    if int(dm_id) not in dm_id_list:
        valid_dm = False
    if valid_dm == False and valid_channel == False:
        raise InputError("Invalid channel and DM IDs")

# Checking for tags in the optional message in addition to the shared message, 
# if the message is being shared to a channel
def tags_in_shared_message_channel(token, message, name, channel_id):
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []

    # checking to see if the additional message contained tags
    for i in range(len(message)):
        if message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check that the handle belongs to a valid user in the given channel
                if handle_check_channel(handle, channel_id) != None:
                    # creating a notification dictionary for the user
                    notification_dict = {
                        'channel_id': channel_id,
                        'dm_id': -1,
                        'notification_message': f'{auth_user_handle} tagged you in {name}: {message[:20]}'
                    }
                    # adding the notification
                    add_notification(notification_dict, handle_check_channel(handle, channel_id))
                    handle_list.append(handle)

# Checking for tags in the optional message in addition to the shared message, 
# if the message is being shared to a DM
def tags_in_shared_message_dm(token, message, name, dm_id):
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []

    # checking to see if the additional message contained tags
    for i in range(len(message)):
        if message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check that the handle belongs to a valid user in the given channel
                if handle_check_dm(handle, dm_id) != None:
                    # creating a notification dictionary for the user
                    notification_dict = {
                        'channel_id': -1,
                        'dm_id': dm_id,
                        'notification_message': f'{auth_user_handle} tagged you in {name}: {message[:20]}'
                    }
                    # adding the notification
                    add_notification(notification_dict, handle_check_dm(handle, dm_id))
                    handle_list.append(handle)

# Update timestamps data store whenever a user sends a message
def timestamps_update_sent_message(auth_user_id):
    data = data_store.get()
    time_sent = int(datetime.now().timestamp())
    users = data['timestamps']['users']
    workspace = data['timestamps']['workspace']
    # update users
    for i in range(len(users)):
        if users[i]['u_id'] == auth_user_id:
            num_messages_sent = users[i]['messages_sent'][-1]['num_messages_sent'] + 1
            messages_sent_dict = {
                'num_messages_sent': num_messages_sent,
                'time_stamp': time_sent
            }
            users[i]['messages_sent'].append(messages_sent_dict)
    # update workspace
    num_messages_sent = workspace['messages_exist'][-1]['num_messages_exist'] + 1
    messages_sent_dict = {
        'num_messages_exist': num_messages_sent,
        'time_stamp': time_sent
    }
    workspace['messages_exist'].append(messages_sent_dict)

    data_store.set(data)

# Update timestamps data store whenever a user removes a message
def timestamps_update_removed_message():
    data = data_store.get()
    time_removed = int(datetime.now().timestamp())
    workspace = data['timestamps']['workspace']

    # update workspace
    num_messages_sent = workspace['messages_exist'][-1]['num_messages_exist'] - 1
    messages_sent_dict = {
        'num_messages_exist': num_messages_sent,
        'time_stamp': time_removed
    }
    workspace['messages_exist'].append(messages_sent_dict)
    
    data_store.set(data)

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

    # checks for exceptions
    token_check(token)    
    valid_dm_id(dm_id) 
    valid_message_length(message)
    check_dm_member(token, dm_id)
    
    # assigning the message ID
    message_id = number_of_messages() + 1

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }

    # finding the DM with given dm_id and appending the message to the DM's details
    for i in range(len(dm_details)):
        if dm_details[i]['dm_id'] == int(dm_id):
            dm_details[i]['messages'].append(message_dict)
            data_store.set(data)
            name = dm_details[i]['name']
    
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []

    # determining whether the message contains any tags
    for i in range(len(message)):
        if message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check if the handle belongs to a valid user in the DM
                if handle_check_dm(handle, dm_id) != None:
                    # creating a notification dictionary for the user
                    notification_dict = {
                        'channel_id': -1,
                        'dm_id': dm_id,
                        'notification_message': f'{auth_user_handle} tagged you in {name}: {message[:20]}'
                    }
                    # adding the notification
                    add_notification(notification_dict, handle_check_dm(handle, dm_id))
                    handle_list.append(handle)

    # updating timestamps store
    timestamps_update_sent_message(auth_user_id)

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
    channel_details = data['channels_details']

    # checks for exceptions
    token_check(token)    
    check_channel(channel_id)
    valid_message_length(message)
    not_a_member(auth_user_id, channel_id)
     
    # assigning the message ID
    message_id = number_of_messages() + 1

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }

    # finding the channel with given channel_id and appending the message to the channel's details
    for i in range(len(channel_details)):
        if int(channel_details[i]['channel_id']) == int(channel_id):
            channel_details[i]['messages'].append(message_dict)
            data_store.set(data)
            name = channel_details[i]["name"]
    
    # obtaining the authorised user's handle
    auth_user_handle = find_handle(token)

    # creating a list of handles to avoid repeats
    handle_list = []

    # determining whether the message contains any tags
    for i in range(len(message)):
        if message[i] == '@':
            x = re.search('@([a-z]){2,}([0-9])*', message[i:])
            handle = x.group()[1:]
            # ensure the handle has not already been tagged in the same message
            if handle not in handle_list:
                # check that the handle belongs to a valid user in the channel
                if handle_check_channel(handle, channel_id) != None:
                    # creating a notification dictionary for the user
                    notification_dict = {
                        'channel_id': channel_id,
                        'dm_id': -1,
                        'notification_message': f'{auth_user_handle} tagged you in {name}: {message[:20]}'
                    }
                    # adding the notification
                    add_notification(notification_dict, handle_check_channel(handle, channel_id))
                    handle_list.append(handle)

    # updating timestamps store
    timestamps_update_sent_message(auth_user_id)

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
    token_check(token)
    valid_message_length_edit(message)
    valid_message_id(token, message_id)
    conditional_edit(token, message_id)
    
    # obtaining what channel/DM the message is in 
    a, b, _, d = return_info(message_id)

    index = False
    # the message is in a DM
    if b == 'dm':
        index = False
        for i in range(len(dm_details)):
            if dm_details[i]['dm_id'] == a:
                messages = dm_details[i]['messages']
                name = dm_details[i]['name']
        # check if the message contained a tag
        edit_with_tags_check_dm(d, message, name, a, token)
    # the message is in a channel
    else:
        index = False 
        for i in range(len(channel_details)):
            if channel_details[i]['channel_id'] == a:
                messages = channel_details[i]['messages']
                name = channel_details[i]['name']
        # check if the message contained a tag
        edit_with_tags_check_channel(d, message, name, a, token)
    # editing the message
    for j in range(len(messages)):
        # find the message
        if messages[j]['message_id'] == int(message_id):
            # if the new message is an empty string, delete the message
            if message == "":
                index = True
                message_index = j
            # otherwise, replace the message with the new text
            else:
                messages[j]['message'] = message
                data_store.set(data)
    if index == True:
        del messages[message_index]
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
    token_check(token)
    valid_message_id(token, message_id)
    conditional_remove(token, message_id)
    
    # obtaining what channel/DM the message is in 
    a, b, *_ = return_info(message_id)

    # the message is in a DM
    if b == 'dm':
        index = False
        for i in range(len(dm_details)):
            if int(dm_details[i]['dm_id']) == a:  
                messages = dm_details[i]['messages']
    # the message is in a channel
    else:
        index = False
        for i in range(len(channel_details)):
            if channel_details[i]['channel_id'] == a:
                messages = channel_details[i]['messages']
    # removing the message
    for j in range(len(messages)):
        # find the message
        if messages[j]['message_id'] == int(message_id):
            index = True
            message_index = j
    if index == True:
        del messages[message_index]
    data_store.set(data)

    # updating timestamps store
    timestamps_update_removed_message()

    return {}

def message_pin_v1(token, message_id):
    """
    Given a message within a channel or DM, pin it

    Arguments:
            token (string) - the token of a authorised user
            message_id (integer) - the ID of a message

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - the message is already pinned
        AccessError - the authorised user does not have owner permissions in the channel/DM

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
    # obtaining data
    data = data_store.get()
    dms = data['dms_details']
    channels = data['channels_details']

    # checks for exceptions
    token_check(token)
    valid_message_id(token, message_id)
    if owner_permissions(token, message_id) ==  False:
        raise AccessError("You do not have access to pin the message")

    # obtaining what channel/DM the message is in 
    a, b, *_ = return_info(message_id)

    # the message is in a channel
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == a:
                messages = channels[i]['messages']
    # the message is in a DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == a:
                messages = dms[i]['messages']
    # marking the message as 'pinned'
    for j in range(len(messages)):
        if messages[j]['message_id'] == message_id:
            if messages[j]['is_pinned'] == True:
                raise InputError(description="Message is already pinned")
            else:
                messages[j]['is_pinned'] = True
    return {}

def message_unpin_v1(token, message_id):
    """
    Given a message within a channel or DM, unpin it

    Arguments:
            token (string) - the token of a authorised user
            message_id (integer) - the ID of a message

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - the message is not already pinned
        AccessError - the authorised user does not have owner permissions in the channel/DM

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
     # obtaining data
    data = data_store.get()
    dms = data['dms_details']
    channels = data['channels_details']

    # checks for exceptions
    token_check(token)
    valid_message_id(token, message_id)
    if owner_permissions(token, message_id) ==  False:
        raise AccessError("You do not have access to unpin the message")

    # obtaining what channel/DM the message is in 
    a, b, *_ = return_info(message_id)

    # the message is in a channel
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == a:
                messages = channels[i]['messages']
    # the message is in a DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == a:
                messages = dms[i]['messages']
    # removing the pin from the message
    for j in range(len(messages)):
        if messages[j]['message_id'] == message_id:
            if messages[j]['is_pinned'] == False:
                raise InputError(description="Message is not pinned")
            else:
                messages[j]['is_pinned'] = False
    return {}

def message_react_v1(token, message_id, react_id ):
    """
    Given a message, a react is added to that message.

    Arguments:
            token (string) - the token of a authorised user
            message_id (integer) - the ID of a message
            react_id (integer) - the ID of a react 

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - react_id is not a valid react ID
        InputError -  the message already contains a react from the authorised user

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
    # obtaining data
    data = data_store.get()
    auth_user_id = decode_JWT(token)['u_id']
    channels = data['channels_details']
    dms = data['dms_details']
    handle = find_handle(token)

    # checks for exceptions
    token_check(token)
    valid_message_id(token, message_id)
    if int(react_id) != 1:
        raise InputError(description="Invalid react")

    # obtaining what channel/DM the message is in 
    a, b, c, _ = return_info(message_id)

    # the message is in a channel
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == a:
                messages = channels[i]['messages']
                name = channels[i]['name']
        notification_dict = {
            'channel_id': a,
            'dm_id': -1,
            'notification_message': f'{handle} reacted to your message in {name}'
        }   
    # the message is in a DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == a:
                messages = dms[i]['messages']
                name = dms[i]['name']
        notification_dict = {
            'channel_id': -1,
            'dm_id': a,
            'notification_message': f'{handle} reacted to your message in {name}'
        }   
    # adding the user to the list of users who have reacted to the given message
    for j in range(len(messages)):
        if messages[j]['message_id'] == message_id:
            if auth_user_id in messages[j]['reacts'][0]['u_ids']:
                raise InputError(description="You have already reacted to this message")
            else:
                messages[j]['reacts'][0]['u_ids'].append(auth_user_id)
    
    # adding a notification for the user who sent the message
    add_notification(notification_dict, c)

def message_unreact_v1(token, message_id, react_id ):
    """
    Given a message with a react, the react is removed.

    Arguments:
            token (string) - the token of a authorised user
            message_id (integer) - the ID of a message
            react_id (integer) - the ID of a react 

    Exceptions: 
        InputError - message_id does not refer to a valid message within a channel/DM
        InputError - react_id is not a valid react ID
        InputError -  the message does not already contain a react from the authorised user

    Return Value:
        Returns an empty dictionary on all valid conditions. 
    """
    # obtaining data
    data = data_store.get()
    dms = data['dms_details']
    channels = data['channels_details']
    auth_user_id = decode_JWT(token)['u_id']

    # checks for exceptions
    token_check(token)
    valid_message_id(token, message_id)
    if int(react_id) != 1:
        raise InputError("Invalid react")
    
    # obtaining what channel/DM the message is in 
    a, b, *_ = return_info(message_id)

    # the message is in a channel
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == a:
                messages = channels[i]['messages']
    # the message is in a DM
    else:
        for i in range(len(dms)):
            if dms[i]['dm_id'] == a:
                messages = dms[i]['messages']
    # removing the user to the list of users who have reacted to the given message
    for j in range(len(messages)):
        if messages[j]['message_id'] == message_id:
            if auth_user_id not in messages[j]['reacts'][0]['u_ids']:
                raise InputError(description="You have not reacted to this message")
            else:
                messages[j]['reacts'][0]['u_ids'].remove(auth_user_id)

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    Given a message ID, share the message into the specified channel/DM with an optional additional message.

    Arguments:
            token (string) - the token of a authorised user
            og_message_id (integer) - the ID of a message
            message (string) - the optional additional message to be sent
            channel_id (integer) - the ID of an existing channel
            dm_id (integer) - the ID of an existing DM

    Exceptions: 
        InputError - both channel_id and dm_id are invalid
        InputError - neither channel_id nor dm_id are -1
        InputError - og_message_id does not refer to a valid message within the channel/DM the authorised user has joined
        InputError - length of message is over 1000 characters
        AccessError - the authorised user has not joined the channel/DM they are trying to share the message to

    Return Value:
        Returns 'shared_message_id' on all valid conditions
    """
    # obtaining data
    data = data_store.get()
    auth_user_id = decode_JWT(token)['u_id']
    channel_details = data['channels_details']
    dm_details = data['dms_details']

    # checks for exceptions
    token_check(token)
    valid_message_id(token, og_message_id)
    valid_message_length_edit(message)
    check_valid_channel_and_dm_id(channel_id, dm_id)
    if channel_id != -1 and dm_id != -1:
        raise InputError(description="Invalid channel and DM IDs")
    if channel_id == -1:
        check_dm_member(token, dm_id)
    else:
        not_a_member(auth_user_id, channel_id)
    
    # assigning the message ID
    shared_message_id = number_of_messages() + 1

    # obtaining the time the message is shared
    time = datetime.now()
    time_shared = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # finding the original message
    *_, og_message = return_info(og_message_id)

    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': shared_message_id,
        'u_id': auth_user_id,
        'message': og_message + message ,
        'time_created': time_shared,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }

    # sharing the message to a channel
    if channel_id != -1:
        # find the channel and append the shared message to the channel's messages
        for i in range(len(channel_details)):
            if channel_details[i]['channel_id'] == int(channel_id):
                name = channel_details[i]['name']
                channel_details[i]['messages'].append(message_dict)
                data_store.set(data)
                # checking if the additional message contains tags
                tags_in_shared_message_channel(token, message, name, int(channel_id))
    
    # sharing the message to a DM
    else:
        for i in range(len(dm_details)):
            if dm_details[i]['dm_id'] == int(dm_id):
                name = dm_details[i]['name']
                dm_details[i]['messages'].append(message_dict)
                data_store.set(data)
                # checking if the additional message contains tags
                tags_in_shared_message_dm(token, message, name, dm_id)

    # updating timestamps store
    timestamps_update_sent_message(auth_user_id)
    
    return {'shared_message_id': shared_message_id}
