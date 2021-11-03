from src.data_store import data_store
from src.token_helpers import generate_new_session_id, generate_JWT, decode_JWT

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

    # find channels joined 






    return 

def users_stats_v1():
    






