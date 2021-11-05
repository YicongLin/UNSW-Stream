from src.data_store import data_store
from src.dm import is_valid_token
from src.error import AccessError, InputError
from src.message import message_send_v1, message_senddm_v1
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
    
    is_valid_token(token)
    is_valid_channel(channel_id)
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600
    if (time_sent < time_created):
        raise InputError(description="Can't send messages to the past!")

    
    while True:
        time = datetime.now()
        if (time == time_sent):
            message_id = message_send_v1(token, channel_id, message)
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