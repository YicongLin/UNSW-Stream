from src.data_store import data_store
from src.error import InputError

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
    return {
        'channel_id': 1,
    }

