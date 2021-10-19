from src.data_store import data_store
from src.error import AccessError, InputError

def check_duplicate(list, channel):

    # check for the element passed in is in the list or not
    i = 0
    while i < len(list):
        if (channel == list[i]):
            return 1
        i += 1
    return 0
    
def channels_list_v1(auth_user_id):
    """Provide a list of all channels that the authorised user is part of.
    
    Arguments:
        auth_user_id (integer) - the ID of an authorised user

    Exceptions:
        AccessError - Occurs when user type in an invalid id

    Return Value:
        a list of dictionaries, where  { channel_id, name }. channel_id(integer) is channels id
        name(string) of the channel.
    """
    
    data = data_store.get()
    channel_info = data['channels']
    channel_detail_info = data['channels_details']
    users_info = data['users']
    found_channel = []
    
    flag = 0
    count = 0
    while count < len(users_info):
        if (users_info[count]['u_id'] == auth_user_id):
            flag = 1
        count += 1
    if (flag == 0):
        raise AccessError("Invalid ID")

    # looks for the users in channel detail by checking the channel members in each channel
    users = 0
    while users < len(channel_detail_info):
        channel_member_info = channel_detail_info[users]['channel_members']
        # if an user id matches the given id, save that id and got to channels datastore
        member = 0
        flag1 = 0
        while member < len(channel_member_info):
            # check each member's user id, if it is the same as given id save the current channel id
            if (channel_member_info[member]['u_id'] == auth_user_id):
                channel_id_info = channel_detail_info[users]['channel_id']
                flag1 = 1
            member += 1
            # if id found, go to channels datastore and loop through to find the samw channel id and append 
            # to the list. otherwise continue
            if (flag1 == 1):
                channels = 0
                while channels < len(channel_info):
                    if (channel_id_info == channel_info[channels]['channel_id']):
                        if (check_duplicate(found_channel, channel_info[channels]) != 1):
                            found_channel.append(channel_info[channels])
                    channels += 1   
        users += 1
    
    data_store.set(data)
    
    return {
        'channels': found_channel
    }

def channels_listall_v1(auth_user_id):
    """An authorised user to check all existed channels
    
    Arguments:
        auth_user_id (integer) - the ID of an authorised user

    Exceptions:
        AccessError - Occurs when user type in an invalid id

    Return Value:
        a list of dictionaries, where  { channel_id, name }.
        channel_id(integer) is channels id
        name(string) of the channel.
    """

    # Obtain data already existed
    data = data_store.get()

    # Test auth_user_id valid or not
    # Collect ids store in the users dict
    users_data = data['users']
    users_element = 0
    users_id = []
    while users_element < len(users_data):
        each_dict = users_data[users_element]
        users_id.append(each_dict['u_id'])
        users_element += 1     
        
    if auth_user_id not in users_id:
        raise AccessError("Invalid ID")
    
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

    # check for invalid name
    if len(name) > 20:
        raise InputError("Invalid name: Too long")
    elif len(name) == 0:
        raise InputError("Invalid name: Too short")

    # get data from datastore
    data = data_store.get()
    users_info = data['users']
    channels_info = data['channels']
    new_channel_id = len(channels_info) + 1
    
    # check for invalid id
    count = 0
    users_id = []
    while count < len(users_info):
        each_dict = users_info[count]
        users_id.append(each_dict['u_id'])
        count += 1

    if auth_user_id not in users_id:
        raise AccessError("Invalid ID")
    
    """ 
    for owner in users_info:
        # since user id = counter - 1, for example 1st user's id is 1 and it is equal to users[0]['id']
        if (users_info[owner]['first_name'] == users_info[auth_user_id - 1]['first_name']):
            owner_first_name = users_info[owner]['first_name']
        if (users_info[owner]['last_name'] == users_info[auth_user_id - 1]['last_name']):
            owner_last_name = users_info[owner]['last_name']
        if (users_info[owner]['email'] == users_info[auth_user_id - 1]['last_name']):
    """
    
    # a dictionary for the channel
    channels_dict = {
        'channel_id': new_channel_id,
        'name': name
    }

    channels_detail_dict = {
        'channel_id': new_channel_id,
        'channel_name': name,
        'channel_status': is_public,
        'owner_members': [
            users_info[auth_user_id - 1]
        ],
        'channel_members': [
            users_info[auth_user_id - 1]
        ]
    }
    
    # append all data and return
    data['channels'].append(channels_dict)
    data['channels_details'].append(channels_detail_dict)
    data_store.set(data)
    return { "channel_id": new_channel_id }

def dm_create_v1(token, u_ids):
    data = data_store.get()
    users = data['users']
    dm = data['dms']

    if (check_user(users, u_ids) == 0):
        raise InputError("There is 1 or more invalid ids, please check again")
    
    new_dm_id = len(dm) + 1

    handle_str = get_name(users, u_ids)
    member_detail = get_member_detail(users, u_ids)

    dm_detail_dict = {
        'dm_id': new_dm_id,
        'name': handle_str,
        'members': member_detail
    }

    dms_dict = {
        'dm_id': new_dm_id,
        'name': handle_str
    }

    data['dms'].append(dms_dict)
    data['dms_details'].append(dm_detail_dict)
    return {
        'dm_id': new_dm_id
    }

# a function to check if the user in u_ids is a valid user
def check_user(auth_users, u_ids):
    """ i = 0
    
    while i < len(u_ids):
        j = 0
        flag = 0
        while j < len(auth_users):
            if (u_ids[i] == auth_users[j]['u_id']):
                flag == 1
            j += 1
        if (flag == 0):
            return 0
        i += 1
    
    return 1 """
    user_id_list = []
    a = 0
    while a < len(auth_users):
        user_id_list.append(auth_users[a]['u_id'])
        a += 1
    b = 0
    while b < len(u_ids):
        if (u_ids[b] not in user_id_list):
            return 0
        b += 1
    return 1 
# get the members details that on the list passed in
def get_member_detail(users_dict, id_list):
    user_detail_list = []
    
    i = 0
    while i < len(id_list):
        j = 0
        while j < len(users_dict):
            if (id_list[i] == users_dict[j]['u_id']):
                user_detail_list.append(users_dict[j])
            j += 1
        i += 1
    return user_detail_list

# get every users'handle_str and append them in a list
def get_name(users_dict, id_list):
    names_list = []
    i = 0
    while i < len(id_list):
        j = 0
        while j < len(users_dict):
            if (id_list[i] == users_dict[j]['u_id']):
                names_list.append(users_dict[j]['handle_str'])
            j += 1
        i += 1
    names_list = sorted(names_list)
    return names_list