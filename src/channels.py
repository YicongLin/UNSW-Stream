from src.data_store import data_store
from src.error import AccessError

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
        users_id.append(each_dict['user_id'])
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
    if len(name) > 20:
        raise InputError("Invalid name: Too long")
    elif len(name) == 0:
        raise InputError("Invalid name: Too short")

    data = data_store.get()
    users_info = data['users']
    count = 0
    while count < len(users_info):
        channel_id = users_info[count]
        if (channel_id['u_id'] == auth_user_id):
            data['channels'].append(auth_user_id, name, is_public)
        count += 1
    data_store.set(data)
    return {
        'channel_id': auth_user_id
    }


