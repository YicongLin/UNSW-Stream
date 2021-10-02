from src.data_store import data_store
from src.error import AccessError, InputError

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
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
    flag = 0
    for user in users_info:
        if (users_info[user]['user_id'] == auth_user_id):
            flag = 1

    if (flag == 0):
        raise AccessError("Invalid ID")
    # find owner name
    owner_first_name = users_info[auth_user_id - 1]['first_name']
    owner_last_name = users_info[auth_user_id - 1]['last_name']
    owner_email = users_info[auth_user_id - 1]['email']
    handle_str = owner_first_name + owner_last_name
    """ for owner in users_info:
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
        'channel_name': name
    }

    channels_detail_dict = {
        'u_name': owner_first_name,
        'is_public': is_public,
        'owner_members': [
            {
                'u_id': auth_user_id,
                'email': owner_email,
                'name_first': owner_first_name,
                'name_last': owner_last_name,
                'handle_str': handle_str.lower()
            }
        ],
        'all_members': [
            {
                'u_id': auth_user_id,
                'email': owner_email,
                'name_first': owner_first_name,
                'name_last': owner_last_name,
                'handle_str': handle_str.lower()
            }
        ]
    }
    # append all data and return
    data['channels'].append(channels_dict)
    data['channels_details'].append(channels_detail_dict)
    data_store.set(data)
    return {
        new_channel_id
    }


