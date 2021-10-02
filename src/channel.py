from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

 
def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }
    
 

def channel_join_v1(auth_user_id, channel_id):

    # Accessing contents of the data store
    data = data_store.get()
    
    # Assumption: a valid and authorised user ID is provided
   
    # Creating a list of all valid channel IDs.
    channels = data["channel_details"]
    valid_channel_ids = []
    for channel in channels:
        valid_channel_ids.append(channel["channel_id"])
        
    # Raising an error if the given channel ID is not 
    # a valid channel in the created list
    if channel_id not in valid_channel_ids:
        raise InputError("Invalid channel_id")
    
    # Raising an error if the authorised user is already a member of the channel
    i = 0
    for channel in channels:
        if channel_id == channel["channel_id"]:
            break
        i += 1
    given_channel = channels[i]
    given_channel_members = given_channel["channels_members"]
    for member in given_channel_members:
        if auth_user_id == member["u_id"]:
            raise InputError("Already in channel")
    
    # Raising an error if the channel is private
    given_channel_status = given_channel["channel_status"]
    if given_channel_status != TRUE:
        raise AccessError("Channel is private") 
   
    
    
    
    
    
    
        
    
    
    
    
    
    
     
    



    
    return {
    }
