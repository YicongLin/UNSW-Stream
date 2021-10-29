from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from datetime import datetime
from src.channel import check_valid_token, check_valid_channel_id, check_member
import hashlib
import jwt

# HELPER FUNCTIONS
# ==================================

# Returns false if the dm_id is invalid
def valid_dm_id(dm_id):
    data = data_store.get()
    dm_details = data['dms_details']
    dm_ids_list = []
    for i in range(len(dm_details)):
        dm_ids_list.append(dm_details[i]['dm_id'])
    if dm_id not in dm_ids_list:
        return
    
    raise InputError(description = "Invalid dm_id" )

# Returns false if the message length is less than 1 or greater than 1000 characters
def valid_message_length(message):
    if len(message) < 1 or len(message) > 1000:
        return 
    
    raise InputError(desctiption = "Invalid message length")

# Returns false if the authorised user is not a member of the DM
def check_dm_member(token):
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']
    dm_members = data['dms_details']['dm_members']
    dm_members_list = []
    for i in range(len(dm_members)):
        dm_members_list.append(dm_members[i]['u_id'])
    if auth_user_id not in dm_members_list:
        return AccessError(description = "Authorised user is not a member of the DM")

# Returns false if the message_id is invalid, or
# Returns the channel/dm ID the message is in, with relevant information
def valid_message_id(message_id):
    data = data_store.get()
    channels = data['channels_details']
    dms = data['dms_details']

    for i in range(len(channels)):
        channel_messages = channels[i]['messages']
        for j in range(len(channel_messages)):
            if channel_messages[j]['message_id'] == message_id:
                return channels[i]['channel_id'], 'channel', channels[j]['u_id']
    for i in range(len(dms)):
        dm_messages = dms[i]['messages']
        for j in range(len(dm_messages)):
            if dm_messages[j]['message_id'] == message_id:
                return dms[i]['dm_id'], 'dm', dms[j]['u_id']
    return False, False, False

# Returns false if the authorised user doesn't have owner permissions 
# in the channel/DM that a given message is in
def owner_permissions(token):
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']
    channels = data['channels_details']
    dms = data['dms_details']

    a, b, c = valid_message_id(message_id)
    owner_members_list1 = []
    if b == 'channel':
        for i in range(len(channels)):
            if channels[i]['channel_id'] == a:
                owner_members = channels[i]['owner_members']
                for j in range(len(owner_members)):
                    owner_members_list.append(owner_members[j]['u_id'])
    if  auth_user_id not in owner_members_list:
        return False
    if b == 'dm':
        for i in range(len(dms)):
            if dms[i]['dm_id'] == a:
                creator = dms[i]['creator']
                if creator['u_id'] != auth_user_id:
                    return False

# Returns false if none of the following conditions are true:
# - the message was sent by the authorised user
# - the authorised user has owner permisisons in the channel/DM
def conditional_edit(token, message_id):
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

    a, b, c = valid_message_id(message_id)
    if c != auth_user_id and owner_permissions(token) == False:
        return 
    
    raise AccessError(description = "User is not authorised to make this request")

# ==================================
# FUNCTIONS

def message_senddm_v1(token, dm_id, message):

    """Send a message from the authorised user to the specified DM.
   
    Arguments:
        token (string) - the token of a authorised user
        dm_id (integer) - the ID of an existing DM
        message (string) - message to be sent
       
    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid channel
        InputError - Occurs when the message length is invalid
        AccessError - Occurs when the authorised user is not a member of the valid DM
    
    Return Value:
        Returns message_id on all valid conditions
    """
    #Obtaining data
    data = data_store.get()

    # Check for invalid token
    if check_valid_token(token) == False:
        raise AccessError("Invalid token")
    
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

    # Check for valid dm_id
    if valid_dm_id(dm_id) == False:
        raise InputError("Invalid DM")
    
    # Check for valid message length
    if valid_message_length(message) == False:
        raise InputError("Invalid message length")
    
    # Raise an error if the authorised user is not a member of the DM
    if check_dm_member(token) == False:
        raise AccessError("Not a member of the DM")
    
    # Otherwise, send the message to the specified DM

    # Obtain the total number of messages existing in order to assign a message ID
    length_of_messages = 0
    dm_details = data['dms_details']
    channel_details = data['channels_details']
    for i in range(len(dm_details)):
        length_of_messages += len(dm_details[i]['messages'])
    for i in range(len(channel_details)):
        length_of_messages += len(channel_details[i]['messages'])
 
    # Assigning the message ID
    message_id = length_of_messages + 1

    # Obtaining time created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # Creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created,
    }
    
    return {message_id}

# function for sending messages
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
 
    #Obtaining data
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

    # Check for valid channel_id
    if check_valid_channel_id(channel_id) == False:
        raise InputError("Invalid channel")
    else:
        channel_id_index = check_valid_channel_id(channel_id)
    
    # Check for valid message length
    valid_message_length = valid_message_length(message)
    if valid_message_length == False:
        raise InputError("Invalid message length")
    
    # Raise an error if the authorised user is not a member of the channel
    if check_member(channel_id_index, auth_user_id) == False:
        raise AccessError("Not a member of the channel")
    
    # Otherwise, send the message to the specified DM

    # Obtain the total number of messages existing in order to assign a message ID
    length_of_messages = 0
    dm_details = data['dms_details']
    channel_details = data['channels_details']
    length_of_messages += len(channels_details['messages'])
    length_of_messages += len(channels_details['messages'])

    # Assigning the message ID
    message_id = length_of_messages + 1

    # Obtaining time created
    time = datetime.now()
    time_created = time.replace(tzinfo=timezone.utc).timestamp()

    # Creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': time_created
    }
    
    return {message_id}

# function for editing messages
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
# Obtaining data
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

# Checking that length of messages are over 1 and under 1000 characters 
    valid_message_length = valid_message_length(message)
    if valid_message_length == False:
        raise InputError("Invalid message length")

# Checking that message_id refers to a valid message
    valid_message_id = valid_message_id(message_id)
    if valid_message_id == False:
        raise InputError("Invalid message")

# Checking that the message was sent by the authorised user making the request 
# and that the authorised user has owner permissions 
    conditional_edit = conditional_edit(token, message_id)
    if conditional_edit == False:
        raise AccessError("Do not have access to edit message")

# Editing the message in a dm
    dm_details = data['dms_details']
    for i in range(len(dm_details)):
        length_of_messages += len(dm_details[i]['messages'])
    unedited_messages = data[dm_details]['messages']
    unedited_messages['message'] = edited_message

# Editing the message in a channel
    channel_details = data['channels_details']
    for i in range(len(dm_details)):
        length_of_messages += len(channel_details[i]['messages'])
    undeleted_channel_messages = data[channel_details]['messages']
    undeleted_channel_messages['message'].remove(message)  
    
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
# Obtaining data
    data = data_store.get()
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

# Checking that message_id refers to a valid message
    valid_message_id = valid_message_id(message_id)
    if valid_message_id == False:
        raise InputError("Invalid message")

# Checking that the message was sent by the authorised user making the request 
# and that the authorised user has owner permissions 
    conditional_edit = conditional_edit(token, message_id)
    if conditional_edit == False:
        raise AccessError("Do not have access to edit message")

# Removing the message from DMS
    dm_details = data['dms_details']
    for i in range(len(dm_details)):
        length_of_messages += len(dm_details[i]['messages'])
    undeleted_dm_messages = data[dm_details]['messages']
    undeleted_dm_messages['message'].remove(message)  

#Removing the message from channels
    channel_details = data['channels_details']
    for i in range(len(channel_details)):
        length_of_messages += len(channel_details[i]['messages'])
    undeleted_channel_messages = data[channel_details]['messages']
    undeleted_channel_messages['message'].remove(message)  

    return {}
