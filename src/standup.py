from src.data_store import data_store
from src.error import InputError, AccessError
from src.channel import check_valid_token, check_valid_channel_id, check_member
from datetime import datetime, timezone
import math
# ============================================================
# ===========(Raise errors and associate functions)===========
# ============================================================

# ==================================
# Check authorised user type in a valid time for standup function
# If authorised user type in a negative length then raise a InputError
# If authorised user type in a valid then pass this helper function
def check_valid_length(length):
    if int(length) < 0:
        raise InputError(description="Time length shouldnt be negative")

    pass
#Finish valid length check
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
    


    # obtaining the time right now to calculate time_finish
    time = datetime.now()
    time_finish = int(time.replace(tzinfo=timezone.utc).timestamp()) + int(length)


    return {
        "time_finish": time_finish
    }


def standup_active_v1(token, channel_id):
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

    return{
        "is_active": ,
        "time_finish": 
    }
