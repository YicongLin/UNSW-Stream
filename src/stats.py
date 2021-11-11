from src.data_store import data_store
from src.token_helpers import generate_new_session_id, generate_JWT, decode_JWT
from src.channels import channels_list_v2, channels_listall_v2
from src.dm import dm_list_v1
from src.users import token_check

def user_stats_v1(token):
    """
    Fetches the required statistics about this user's use of UNSW Streams.

    Arguments:
        Token

    Return:
        User_stats: {
            channels_joined: [{num_channels_joined, time_stamp}],
            dms_joined: [{num_dms_joined, time_stamp}], 
            messages_sent: [{num_messages_sent, time_stamp}], 
            involvement_rate 
    }
    """
    store = data_store.get()
    token_check(token)

    # decode the token to find the user id 
    decoded_token = decode_JWT(token)
    u_id = decoded_token['u_id']

    # number of channels joined 
    channel_list = channels_list_v2(token)
    num_channels_joined = len(channel_list['channels'])

    # number of dms joined 
    dm_list = dm_list_v1(token) 
    num_dms_joined = len(dm_list['dms'])

    # number of messages sent (only increases, removed messages does not affect)
    # messages in channels

    channel_msgs_sent = 0
    i = 0
    while i < len(store['channels_details']):
        j = 0
        while j < len(store['channels_details'][i]['messages']):
            if store['channels_details'][i]['messages'][j]['u_id'] == u_id:
                channel_msgs_sent += 1
            j += 1
        i += 1

    # messages in dms
    i = 0
    j = 0
    dms_msgs_sent = 0
    while i < len(store['dms_details']):
        while j < len(store['dms_details'][i]['messages']):
            if store['dms_details'][i]['messages'][j]['u_id'] == u_id:
                dms_msgs_sent += 1
            j += 1
        i += 1

    # removed messages 
    i = 0
    rem_msgs_sent = 0
    while i < len(store['removed_messages']):
        if store['removed_messages'][i]['u_id'] == u_id:
            rem_msgs_sent += 1
        i += 1

    # total user messages 
    num_msgs_sent = channel_msgs_sent + dms_msgs_sent + rem_msgs_sent

    # current number of channels 
    num_channels = len(store['channels_details'])

    # current number of dms
    num_dms = len(store['dms_details'])

    # current number of messages 
    # loop through dms_details to find total messages
    dms_msgs = 0 
    i = 0
    while i < len(store['dms_details']):
        dms_msgs += len(store['dms_details'][i]['messages'])     
        i += 1

    # loop through channels_details to find total messages 
    channels_msgs = 0 
    i = 0
    while i < len(store['channels_details']):
        channels_msgs += len(store['channels_details'][i]['messages'])     
        i += 1

    # DO NOT LOOP THROUGH REMOVED MESSAGES 
    num_msgs = dms_msgs + channels_msgs

    # involvement rate 
    if (num_channels + num_dms + num_msgs) == 0:
        involvement_rate = 0 
    else: 
        involvement_rate = (num_channels_joined + num_dms_joined + num_msgs_sent)/(num_channels + num_dms + num_msgs)

    if involvement_rate > 1:
        involvement_rate == 1

    return {
        'user_stats' : 
            {
            'channels_joined' : store['timestamps']['users'][u_id - 1]['channels_joined'],
            'dms_joined' : store['timestamps']['users'][u_id - 1]['dms_joined'], 
            'messages_sent': store['timestamps']['users'][u_id - 1]['messages_sent'], 
            'involvement_rate' : involvement_rate
        }
    } 

def users_stats_v1(token):
    """
    Fetches the required statistics about the use of UNSW Streams.
    
    Arguments:
        Token
    
    Return:
        Workspace_stats: {
            channels_exist: [{num_channels_exist, time_stamp}], 
            dms_exist: [{num_dms_exist, time_stamp}], 
            messages_exist: [{num_messages_exist, time_stamp}], 
            utilization_rate 
        }
    """
    token_check(token)
    store = data_store.get()

    # # number of existing channels 
    # channel_list = channels_listall_v2(token)
    # num_channels = len(channel_list)
    
    # # number of existing dms 
    # dm_list = store['dms_details']
    # num_dms = len(dm_list)

    # number of users 
    num_users = len(store['users'])

    # # current number of messages -  number of messages that exist at the current time (can decrease)
    # # loop through dms_details to find total messages
    # dms_msgs = 0 
    # i = 0
    # while i < len(store['dms_details']):
    #     dms_msgs += len(store['dms_details'][i]['messages'])     
    # i += 1

    # # loop through channels_details to find total messages 
    # channels_msgs = 0 
    # i = 0
    # while i < len(store['channels_details']):
    #     channels_msgs += len(store['channels_details'][i]['messages'])     
    # i += 1

    # # DO NOT LOOP THROUGH REMOVED MESSAGES 
    # num_msgs = dms_msgs + channels_msgs

    # users who have joined at least 1 channel or dm 
    
    # create list of u_ids who are in a dm 
    dms_list = [ ]

    i = 0
    while i < len(store['dms_details']):
        j = 0
        while j < len(store['dms_details']['members']):
            current_id = store['dms_details']['members'][j]['u_id'] 
            dms_list.append(current_id)
        j += 1
    i += 1

    channels_list = [ ]
    i = 0
    while i < len(store['channels_details']):
        j = 0
        while j < len(store['channels_details']['channel_members']):
            current_id = store['channels_details']['channel_members'][j]['u_id'] 
            channels_list.append(current_id)
        j += 1
    i += 1

    dms_list_set = set(dms_list)
    common = dms_list_set.intersection(channels_list)

    common_list = list(common)
    num_users_who_have_joined_at_least_one_channel_or_dm = len(common_list)

    # utilization rate 
    utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / num_users

    return {
        'workplace_stats' : 
            {
            'channels_exist': store['timestamps']['workspace']['channels_exist'], 
            'dms_exist': store['timestamps']['workspace']['dms_exist'], 
            'messages_exist': store['timestamps']['workspace']['messages_exist'], 
            'utilization_rate' : utilization_rate
            }
    }


