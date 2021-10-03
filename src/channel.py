from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    # Accessing contents of the data store
    data = data_store.get()
    
    # Creating a list of all valid channel IDs
    channels = data["channels_details"]
    valid_channel_ids = []
    for channel in channels:
        valid_channel_ids.append(channel["channel_id"])
        
    # Raising an error if the given channel ID is not 
    # a valid channel in the created list
    if channel_id not in valid_channel_ids:
        raise InputError("Invalid channel_id")
        
    # Creating a list of all valid user IDs
    users = data["users"]
    valid_user_ids = []
    for user in users:
        valid_user_ids.append(user["user_id"])
  
    # Raising an error if u_id is not a valid user 
    # in the created list
    if u_id not in valid_user_ids:
        raise InputError("Invalid user")
    
    # Raising an error if u_id is already a member of the channel
    channel_count = 0
    for channel in channels:
        if channel_id == channel["channel_id"]:
            break
        channel_count += 1
    members = channels[channel_count]["channel_members"]
    for member in members:
        if u_id == member["user_id"]:
            raise InputError("Already in channel")
    
    # Raising an error if the authorised user 
    # is not a member of the valid channel
    member_of_channel = False
    for member in members:
        if auth_user_id == member["user_id"]:
            member_of_channel = True
    if member_of_channel == False:
        raise AccessError("You are not a member of the channel")

    # Otherwise, add the user to the channel
    
    # Extracting the given user's information
    user_count = 0
    for user in users:
        if user["user_id"] == u_id:
            break
        user_count += 1

    # Appending the user information to the channel
    channels[channel_count]["channel_members"].append(users[user_count])

def channel_details_v1(auth_user_id, channel_id):

     # Obtain data alreaday existed
    data = data_store.get()

     # Test auth_user_id valid or not
    users_data = data['users']
    users_element = 0
    users_id = []
    while users_element < len(users_data):
        each_dict_users = users_data[users_element]
        users_id.append(each_dict_users['id'])
        users_element += 1     
        
    if auth_user_id not in users_id:
            raise AccessError("Invalid ID")
    # Finish valid auth_user_id test
    # ==================================
    # Test Invalid channel_id or not
    # Pick out channl_id
    channels_details_data = data['channels_details']
    channels_members_element = 0
    all_channel_id = []
    while channels_members_element < len(channels_details_data):
        each_channel_details = channels_details_data[channels_members_element]
        all_channel_id.append(each_channel_details['channel_id'])
        channels_members_element += 1

    if channel_id not in all_channel_id:
            raise InputError("Invalid channel_id")
    # Finish authorised user test
    # ==================================
    # Obtain the postition of channel_id for track channel_members within this channel
    channel_id_element = 0
    while channel_id_element < len(all_channel_id):
        if channel_id == all_channel_id[channel_id_element]:
            break
        channel_id_element += 1
 
    # All members' details in this channel
    members_in_channel = channels_details_data[channel_id_element]['members']
    # ==================================
    # Pick out u_id
    # Test user is a member of channel or not
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_channel):
        each_member = members_in_channel[each_member_element]
        each_member_id.append(each_member['u_id'])
        each_member_element += 1 

    if auth_user_id not in each_member_id:
        raise AccessError("No right to access the channel")
    # Finish member users test
    # ==================================
    # For return
    name = members_in_channel[0]['name_first']
    owner_members = [members_in_channel[0]]
    all_members = members_in_channel
    is_public = channels_details_data[channel_id_element]['channels_status']

    return {
        'name': name,
        'is_public': is_public,
        'owner_members': owner_members,
        'all_members': all_members
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

    # Accessing contents of the data store
    data = data_store.get()
   
    # Creating a list of all valid channel IDs.
    channels = data["channels_details"]
    valid_channel_ids = []
    for channel in channels:
        valid_channel_ids.append(channel["channel_id"])
        
    # Raising an error if the given channel ID is not 
    # a valid channel in the created list
    if channel_id not in valid_channel_ids:
        raise InputError("Invalid channel_id")
    
    # Raising an error if the authorised user 
    # is already a member of the channel
    channel_count = 0
    for channel in channels:
        if channel_id == channel["channel_id"]:
            break
        channel_count += 1
    members = channels[channel_count]["channel_members"]
    for member in members:
        if auth_user_id == member["user_id"]:
            raise InputError("Already in channel")
    
    # Raising an error if the channel is private
    if channels[channel_count]["channel_status"] != True:
        raise AccessError("Channel is private") 
        
    # Otherwise, add the user to the channel
  
    # Extracting the given user's information
    users = data["users"]
    user_count = 0
    for user in users:
        if user["user_id"] == auth_user_id:
            break
        user_count += 1

    # Appending the user information to the channel
    channels[channel_count]["channel_members"].append(users[user_count])

