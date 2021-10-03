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
    # Accessing the data store
    data = data_store.get()
    
    # Creating a list of valid channel IDS
    channels = data["channel_details"]
    valid_channel_ids = []
    for channel in channels:
        valid_channel_ids.append(channel["channel_id"])
    
    # Error if channel ID is invalid 
    if channel_id not in valid_channel_ids:
        raise InputError("Invalid channel_id")
    
    # List of valid user IDS
    users = data["users"]
    valid_user_ids = []
    for user in users:
        valid_user_ids.append(user["user_id"])

    # Error if the auth_user is not a member of the valid channel
    members = channels[channel_count]["channel_members"]
    member_of_channel = False
    for member in members:
        if auth_user_id == member["user_id"]:
            member_of_channel = True
    if member_of_channel == False:
        raise AccessError("You are not a member of the channel")

    # Function returns up to 50 messages
    start = int(start)
    max_messages = 50
    messages_total = 0
    
    # Creating dictionary 
    messages_dict = {
        'messages_id' : 1
        'u_id' : 1
        'message' : 'Hello World'
        'time_created' : 1582426789
    }
    
    '''
    # Creating a messages dictionary
    messages_dict = {"message_id", "u_id", "message", "time_created"}
    messages_list = []
    dict_copy = messages_dict.copy()
    messages_list.append(dict_copy)
    '''
    # Check most recent message is 0 and the start is less than number of messages
    if start >= messages_total and start != 0:
        raise InputError("Start is greater than or equal to the total number of messages in the channel")
    
    # Index between start and start + 50
    end = start + max_messages
    if end > total_message:
        # Indicating there are no more messages to load 
        end = -1
        
    return {'messages': messages, 'start': 0, 'end': 50}

'''
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
'''

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
