from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import check_valid_token, check_valid_channel_id, check_member_authorised_user
from datetime import datetime, timezone
from src.token_helpers import decode_JWT
from src.dm import is_valid_token, decode_token, get_name
from src.iter3_message import is_valid_channel, is_channel_member, message_sendlater_v1
from src.message import number_of_messages
import math
import threading
# ============================================================
# ===========(Raise errors and associate functions)===========
# ============================================================

# ==================================
# Check authorised user type in a valid time for standup function
# If authorised user type in a negative length then raise a InputError
# If authorised user type in a valid length then pass this helper function
def check_valid_length(length):
    if int(length) < 0:
        raise InputError(description="Time length shouldnt be negative")

    pass
# Finish valid length check
# ==================================

# ==================================
# Check active standup in the channel
# If an active standup is currently running in the channel then return the dict of running standup
# If no a standup is running in the channel then return True
def check_active_standup(channel_id_element):
    now_time = datetime.now().timestamp()

    data = data_store.get()

    # If no standup has been run in the channel
    if len(data['channels_details'][channel_id_element]['channel_standup']) == 0:
        return True

    lately_standup_element = len(data['channels_details'][channel_id_element]['channel_standup']) - 1
    channel_lately_time_finish = data['channels_details'][channel_id_element]['channel_standup'][lately_standup_element]['time_finish']

    # If no standup has been run in the channel
    if now_time > channel_lately_time_finish:
        return True

    # return the dict of running standup
    else:
        return data['channels_details'][channel_id_element]['channel_standup'][lately_standup_element]
    
# Finish active standup check
# ==================================


# ============================================================
# =====================(Actual functions)=====================
# ============================================================

def standup_start_v1(token, channel_id, length):
    """An authorised user to start a standup in a channel
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
        length (integer) - the seconds that standup run

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user is not a member of that channel
        InputError - Occurs when authorised user type in an invalid channel id
        InputError - Occurs when authorised user type in a negative length
        InputError - Occurs when authorised user try to start a standup when another standup is running

    Return Value:
        {time_finish}
            time_finish (unix timestamp) - the time this standup stop
    """
    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    check_member_authorised_user(channel_id_element, token)

    # Raise an InputError if authorised user type in a negative length
    check_valid_length(length)
    
    # Raise a InputError if an active standup is currently running in the channel
    if check_active_standup(channel_id_element) != True:
        raise InputError(description="A standup is running")
    
    # Obtaining the uid of authorised user who start a standup
    auth_user_id = decode_JWT(token)['u_id']

    # Obtaining the time right now to calculate time_finish
    time_finish = datetime.now().timestamp() + int(length)

    # Store basic info of this standup into a dict
    new_standup = {
        "start_uid": auth_user_id,
        "time_finish": time_finish,
        "standup_message": []
    }

    # Store new_standup to data_store
    data['channels_details'][channel_id_element]['channel_standup'].append(new_standup)
    
    

    # Find the id of the user who start this standup
    standup_starter_uid = get_standup_starter_id(channel_id_element)
    curr_standup_position = len(data['channels_details'][channel_id_element]['channel_standup']) - 1
    message_list = data['channels_details'][channel_id_element]['channel_standup'][curr_standup_position]['standup_message']
    
    # Send messages happen during standup when standup time is finished
    sending = threading.Timer(length, standup_message_send, [standup_starter_uid, channel_id_element, message_list])
    sending.start()

    # Store data into data_store
    data_store.set(data)

    return {
        "time_finish": int(time_finish)
    }


def standup_active_v1(token, channel_id):
    """Show status of status of channel's current standup
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user is not a member of that channel
        InputError - Occurs when authorised user type in an invalid channel id

    Return Value:
        {is_active, time_finish}
            is_active (boolen) - status of channel's current standup
            time_finish (unix timestamp) - the time this standup stop
    """
    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    check_member_authorised_user(channel_id_element, token)

    # Initialize return variables
    is_active = False
    time_finish = None

    # If there is a running standup then change varibales values
    if type(check_active_standup(channel_id_element)) is dict:
        is_active = True
        time_finish = int(check_active_standup(channel_id_element)['time_finish'])

    return {
        "is_active": is_active,
        "time_finish": time_finish
    }


def standup_send_v1(token, channel_id, message):
    """ 
    Sending a message to get buffered in the standup queue, assuming a standup is currently active. 
    Note: We do not expect @ tags to be parsed as proper tags when sending to standup/send
    
    parameter: token, dm_id, message, time_sent
        
        errors: 
            - access: invalid token
            - access: channel_id is valid and the authorised user is not a member of the channel
            - input: 
                    channel_id does not refer to a valid channel
                    length of message is over 1000 characters
                    an active standup is not currently running in the channel

        return value: message_id

    """
    # invalid token
    is_valid_token(token)

    # channel_id does not refer to a valid channel
    # is_valid_channel(channel_id)
    channel_id_element = check_valid_channel_id(channel_id)
    # channel_id is valid and the authorised user is not a member of the channel
    is_channel_member(token, channel_id)

    # length of message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    # an active standup is not currently running in the channel
    standup = standup_active_v1(token, channel_id)
    is_active = standup['is_active']

    if is_active == False:
        raise InputError(description="Stand up is not currently running")
    
    # if type(check_active_standup(channel_id_element)) is dict:
    #     raise InputError(description="Stand up is not currently running")
    data = data_store.get()
    
    
    u_id = decode_token(token)
    
    # find the current position of the standup
    curr_standup_position = len(data['channels_details'][channel_id_element]['channel_standup']) - 1
    
    # get user's handle_str
    user_handle = get_name([u_id])
    
    # update message to the expected format. 
    # eg. before: "hey guys how u going with project"
    # after: "yiconglin: hey guys how u going with project"
    message = user_handle + ": " + message

    # append the above message to the standup message list in the datastore, so it becomes a list of strings
    data['channels_details'][channel_id_element]['channel_standup'][curr_standup_position]['standup_message'].append(message)
        
    data_store.set(data)

    return {}


# check if the user is the person who start the standup
def get_standup_starter_id(channel_id_position):
    
    data = data_store.get()
    if len(data['channels_details']) != 0:
        curr_standup_position = len(data['channels_details'][channel_id_position]['channel_standup']) - 1
        starter_id = data['channels_details'][channel_id_position]['channel_standup'][curr_standup_position]['start_uid']
        return starter_id


def standup_message_send(auth_user_id, channel_id_position, message):
    data = data_store.get()

    message_id = number_of_messages() + 1

    # obtaining the time the message is created
    time = datetime.now()
    time_created = math.floor(time.replace(tzinfo=timezone.utc).timestamp()) - 39600

    # split up messages with a newline
    # eg. before: "yiconglin: hello", "kangliu: world"
    # after: "yiconglin: hello"
    #        "kangliu: world"
    message = "\n".join(message)
    # creating a dictionary with the message and corresponding information
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': f"{message}",
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
    if len(data['channels_details']) != 0:
        data['channels_details'][channel_id_position]['messages'].append(message_dict)
        data_store.set(data)

