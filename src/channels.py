from src.data_store import data_store
from src.error import AccessError, InputError
from src.dm import decode_token, is_valid_token
from src.channel import check_valid_token
def check_duplicate(list, channel):

    # check for the element passed in is in the list or not
    i = 0
    while i < len(list):
        if (channel == list[i]):
            return 1
        i += 1
    return 0
    
def channels_list_v2(token):
    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")
    data = data_store.get()
    channel_detail = data['channels_details']
    user_id = decode_token(token)

    """ if (check_valid_token(token) == False):
        raise AccessError("Invalid user") """

    channel_list = []
    i = 0
    while i < len(channel_detail):
        channel_member = channel_detail[i]['channel_members']
        j = 0
        while j < len(channel_member):
            if (user_id == channel_member[j]['u_id']):
                channel_list.append({
                    'channel_id': channel_detail[i]['channel_id'],
                    'name': channel_detail[i]['name']
                })
            j += 1
        i += 1

    return {
        'channels': channel_list
    }


def channels_listall_v2(token):
    """An authorised user to check all existed channels
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token

    Return Value:
        {channels}
            channels(a list of dict): [{channel_id, name}]

            channel_id (integer) - ID of the channel
            name (string) - name of the channel.
    """

    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Obatin all channels' information
    chan_data = data['channels']
    
    return {'channels': chan_data}

def channels_create_v2(token, name, is_public):
    """An authorised user with auth_user_id, type the name of this channel and whether this channel is public. Return that channel’s id when it s created.

    Arguments:
        auth_user_id (integer) - the ID of an authorised user
        name(string)- channel’s name authorised user deign
        is_public(boolean) - channel’s status (public or private)

    Exceptions:
        AccessError - Occurs when user type in an invalid id
        InputError - Length of channel name is more than 20 or less than 1

    Return Value:
        channel_id(integer) is channels id
    """

    if (is_valid_token(token) == False):
        raise AccessError("Invalid token")

    # get data from datastore
    data = data_store.get()
    users_info = data['users']
    channels_detail = data['channels_details']
    user_id = decode_token(token)
    
    # check for invalid user
    """ if (is_valid_user(user_id) == False):
        raise AccessError("Invalid user") """

    # check for invalid name
    if len(name) > 20:
        raise InputError("Invalid name: Too long")
    elif len(name) == 0:
        raise InputError("Invalid name: Too short")
    
    new_channel_id = len(channels_detail) + 1
    
    # a dictionary for the channel
    channels_dict = {
        'channel_id': new_channel_id,
        'name': name
    }

    channels_detail_dict = {
        'channel_id': new_channel_id,
        'name': name,
        'channel_status': is_public,
        'owner_members': [
            users_info[user_id - 1]
        ],
        'channel_members': [
            users_info[user_id - 1]
        ]
    }
    
    # append all data and return
    data['channels'].append(channels_dict)
    data['channels_details'].append(channels_detail_dict)
    data_store.set(data)
    return { "channel_id": new_channel_id }


