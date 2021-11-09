from src.data_store import data_store
from src.dm import is_valid_token, decode_token
from src.error import AccessError, InputError
from src.message import message_send_v1, message_senddm_v1, check_dm_member
import math
from datetime import timezone, datetime
def message_sendlater_v1(token, channel_id, message, time_sent):
    """ 
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future. 
        
        parameter: token, channel_id, message, time_sent
        
        errors: 
            - access: invalid token
            - access: channel_id is valid and the authorised user is not a member of the channel they are trying to post to
            - input: 
                    channel_id does not refer to a valid channel
                    length of message is over 1000 characters
                    time_sent is a time in the past

        return value: message_id

    """
    # errors check
    is_valid_token(token)
    
    is_valid_channel(channel_id)

    is_channel_member(token, channel_id)
    
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    time = datetime.now()
    # time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    if (time_sent < time):
        raise InputError(description="Can't send messages to the past!")

    
    while True:
        time = datetime.now()
        if (time == time_sent):
            message_id = message_send_v1(token, channel_id, message)
            break

    return {
        'message_id': message_id
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """ 
    Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.
        
        parameter: token, dm_id, message, time_sent
        
        errors: 
            - access: invalid token
            - access: dm_id is valid and the authorised user is not a member of the dm they are trying to post to
            - input: 
                    dm_id does not refer to a valid channel
                    length of message is over 1000 characters
                    time_sent is a time in the past

        return value: message_id

    """
    # errors check
    is_valid_token(token)
    
    is_valid_dm(dm_id)
    
    check_dm_member(token, dm_id)

    
    
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    time = datetime.now()
    # time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    if (time_sent < time):
        raise InputError(description="Can't send messages to the past!")

    while True:
        time = datetime.now()
        if (time == time_sent):
            message_id = message_send_v1(token, dm_id, message)
            break

    return {
        'message_id': message_id
    }


def is_valid_channel(channel_id):
    data = data_store.get()
    channels_details = data['channels_details']

    channel_id_list = []

    i = 0
    while i < len(channels_details):
        channel_id_list.append(channels_details[i]['channel_id'])
        i += 1

    if (channel_id not in channel_id_list):
        raise InputError(description="Invalid Channel Id, please check again")

    return

def is_valid_dm(dm_id):
    data = data_store.get()
    dms_details = data['dms_details']

    dm_id_list = []

    i = 0
    while i < len(dms_details):
        dm_id_list.append(dms_details[i]['dm_id'])
        i += 1

    if (dm_id not in dm_id_list):
        raise InputError(description="Invalid Dm Id, please check again")

    return

def is_channel_member(token, channel_id):
    data = data_store.get()
    channels_details = data['channels_details']
    
    u_id = decode_token(token)
    i = 0
    while i < len(channels_details):
        if (channel_id == channels_details[i]['channel_id']):
            j = 0
            channels_members = channels_details[i]['channel_members']
            while j < len(channels_members):
                if (u_id == channels_members[j]['u_id']):
                    return
                j += 1
        i += 1

    raise AccessError(description="User is not a member of this channel")
