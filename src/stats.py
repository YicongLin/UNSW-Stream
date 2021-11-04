from src.data_store import data_store
from src.token_helpers import generate_new_session_id, generate_JWT, decode_JWT
from src.channels import channels_list_v2, channels_listall_v2
from src.dm import dm_list_v1

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


    # involvement rate 
    if sum(num_channels, num_dms, num_msgs) == 0:
        user_involvement = 0 
    else: 
        user_involvement = sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_channels, num_dms, num_msgs)

    if user_involvement > 1:
        user_involvement == 1


    return 

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
    store = data_store.get()

    # number of existing channels 
    channel_list = channels_listall_v2(token)
    num_channels = len(channel_list)
    
    # number of existing dms 
    dm_list = store['dms_details']
    num_dms = len(dm_list)

    # number of messages -  number of messages that exist at the current time (can decrease)


    # utilization rate 
    utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / num_users

    return 








