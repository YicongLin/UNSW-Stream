from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import check_valid_token, check_valid_channel_id, check_member_authorised_user
from datetime import datetime, timezone
from src.token_helpers import decode_JWT
from src.dm import is_valid_token
from src.iter3_message import is_valid_channel, is_channel_member
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
    now_time = datetime.now().replace(tzinfo=timezone.utc).timestamp()

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
    time_finish = datetime.now().replace(tzinfo=timezone.utc).timestamp() + int(length)

    # Store basic info of this standup into a dict
    new_standup = {
        "start_uid": auth_user_id,
        "time_finish": time_finish
    }

    # Store new_standup to data_store
    data['channels_details'][channel_id_element]['channel_standup'].append(new_standup)
    
    return {
        "time_finish": int(time_finish)
    }


def standup_active_v1(token, channel_id):

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
    is_valid_channel(channel_id)

    # channel_id is valid and the authorised user is not a member of the channel
    is_channel_member(token, channel_id)

    # length of message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    # an active standup is not currently running in the channel
    if check_active_standup(channel_id) == True:
        raise InputError(description="Stand up is not currently running")
    
    return {}