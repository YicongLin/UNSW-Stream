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

    
    users = store['timestamps']['users']
    for i in range(len(users)):
        if users[i]['u_id'] == u_id:
            num_msgs_sent = users[i]['messages_sent'][-1]['num_messages_sent']
    
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

    # number of users 
    num_users = len(store['users'])

    # create list of u_ids who are in a dm 
    dms_list = [ ]
    i = 0
    while i < len(store['dms_details']):
        j = 0
        while j < len(store['dms_details'][i]['members']):
            current_id = store['dms_details'][i]['members'][j]['u_id'] 
            dms_list.append(current_id)
            j += 1
        i += 1

    channels_list = [ ]
    i = 0
    while i < len(store['channels_details']):
        j = 0
        while j < len(store['channels_details'][i]['channel_members']):
            current_id = store['channels_details'][i]['channel_members'][j]['u_id'] 
            channels_list.append(current_id)
            j += 1
        i += 1

    dms_list_set = set(dms_list)
    common = dms_list_set.union(channels_list)

    common_list = list(common)

    num_users_who_have_joined_at_least_one_channel_or_dm = len(common_list)

    # utilization rate 
    if num_users == 0:
        utilization_rate = 0
    else:
        utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / num_users

    return {
        'workspace_stats' : 
            {
            'channels_exist': store['timestamps']['workspace']['channels_exist'], 
            'dms_exist': store['timestamps']['workspace']['dms_exist'], 
            'messages_exist': store['timestamps']['workspace']['messages_exist'], 
            'utilization_rate' : utilization_rate
            }
    }