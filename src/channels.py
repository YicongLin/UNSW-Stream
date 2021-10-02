from src.data_store import data_store
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
    data = data_store.get()
    channel_info = data['channels']
    channel_detail_info = data['channels_details']
    users_info = data['users']
    found_channel = []
    
    
    flag = 0
    count = 0
    while count < len(users_info):
        if (users_info[count]['user_id'] == auth_user_id):
            flag = 1
        count += 1
    if (flag == 0):
        raise AccessError("Invalid ID")

    # looks for the users in channel detail by checking the channel members in each channel
    users = 0
    channels = 0
    member = 0
    flag1 = 0
    while users < len(channel_detail_info):
        channel_member_info = channel_detail_info[users]['channels_members']
        # if an user id matches the given id, save that id and got to channels datastore
        while member < len(channel_member_info):
            if (channel_member_info[member]['u_id'] == auth_user_id):
                channel_id_info = channel_detail_info[users]['channel_id']
                flag1 = 1
            member += 1
            if (flag1 == 1):
                while channels < len(channel_info):
                    if (channel_id_info == channel_info[channels]['channel_id']):
                        found_channel.append(channel_info[channels])
                    channels += 1
        flag1 = 0
        member = 0
        channels = 0    
        users += 1
    
    data_store.set(data)
    
    return {
        'channels': found_channel
        
    }


def channels_listall_v1(auth_user_id):
    # Obtain data alreaday existed
    data = data_store.get()

    # Test auth_user_id valid or not
    # Collect ids store in the users dict
    users_data = data['users']
    users_element = 0
    users_id = []
    while users_element < len(users_data):
        each_dict = users_data[users_element]
        users_id.append(each_dict['id'])
        users_element += 1     
        
    if auth_user_id not in users_id:
            raise InputError("Invalid ID")
    # Finish auth_user_id test

    # Localized channels data, make while loop more easy to look
    chan_data = data['channels']

    # Store channels data into a list for return
    out_channels = []

    i = 0
    while i < len(chan_data):
        out_channels.append(chan_data[i])
        i += 1
    
    return {'channels': out_channels}

def channels_create_v1(auth_user_id, name, is_public):
    if len(name) > 20:
        raise InputError("Invalid name: Too long")
    elif len(name) == 0:
        raise InputError("Invalid name: Too short")

    data = data_store.get()
    users_info = data['users']
    count = 0
    while count < len(users_info):
        channel_id = users_info[count]
        if (channel_id['id'] == auth_user_id):
            data['channels'].append(auth_user_id, name, is_public)
        count += 1
    data_store.set(data)
    return {
        'channel_id': auth_user_id
    }


