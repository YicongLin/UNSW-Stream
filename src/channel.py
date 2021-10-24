from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import hashlib
import jwt
# ============================================================
# ===========(Raise errors and associate functions)===========
# ============================================================

# ==================================
# Check channel_id valid or not
# Serach information at data['channels_details'] 
# If chaneel_id is invalid then return False
# If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
def check_valid_channel_id(channel_id):
    data = data_store.get()

    channels_details_data = data['channels_details']
    channels_members_element = 0
    all_channel_id = []
    while channels_members_element < len(channels_details_data):
        all_channel_id.append(channels_details_data[channels_members_element]['channel_id'])
        channels_members_element += 1

    channel_id_element = 0
    while channel_id_element < len(all_channel_id):
        if channel_id == all_channel_id[channel_id_element]:
            return channel_id_element 
        channel_id_element += 1

    if channel_id not in all_channel_id:
        return False
            
    pass
# Finish authorised user check
# ==================================

# ==================================
# Check u_id valid or not
# Serach information at data['users']
# If u_id is invalid then return False
# If u_id is valid then pass this function
def check_valid_uid(u_id):
    data = data_store.get()

    users_data = data['users']
    users_element = 0
    users_id = []
    while users_element < len(users_data):
        users_id.append(users_data[users_element]['u_id'])
        users_element += 1     
        
    if u_id not in users_id:
        return False

    pass
# Finish valid u_id check
# ==================================

# ==================================
# Check user is a member of channel or not
# Serach information at data['channels_details'][channel_id_element]['channel_members']
# If the user with u_id is not a member of channel then return False
# If the user with u_id is a member of channel then return each_member_id (a list conatins all memebers' u_id)
def check_member(channel_id_element, u_id):
    data = data_store.get()

    members_in_channel = data['channels_details'][channel_id_element]['channel_members']
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_channel):
        each_member_id.append(members_in_channel[each_member_element]['u_id'])
        each_member_element += 1 

    if u_id not in each_member_id:
        return False

    return each_member_id
# Finish member users check
# ==================================

# ==================================
# Provide a list which contains all owners' id within the channel
# Associate with other check_owners functions
def channel_owners_ids(channel_id_element):
    data = data_store.get()

    owner_members_in_channel = data['channels_details'][channel_id_element]['owner_members']
    each_owner_element = 0
    each_owner_id = []
    while each_owner_element < len(owner_members_in_channel):
        each_owner_id.append(owner_members_in_channel[each_owner_element]['u_id'])
        each_owner_element += 1 

    return each_owner_id
# Finish function
# ==================================

# ==================================
# Check token of authorised user is valid or not
# Search information at XXXXXXXX
# def check_token(token):
#     SECRET = 'COMP1531'
#     decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
# Finish authorised user valid token check
# ==================================

# ==================================
# Check authorised user has channel owner permissions or not
# Search information at XXXXXXX
# If authorised user doesn't have channel owener permissions then return False
# Decode details will be moved to config.py
def check_channel_owner_permissions(token, each_owner_id):
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])

    user_permission = decode_token['permission_id']
    auth_user_id = decode_token['u_id']

    if user_permission != 1 and auth_user_id not in each_owner_id:
        return False

    pass
# Finish authorised user permissions check
# ==================================

# ============================================================
# =====================(Actual functions)=====================
# ============================================================

def channel_invite_v1(auth_user_id, channel_id, u_id):
    """An authorised user who is a member of a channel invites
       another user to join the channel.
   
    Arguments:
        auth_user_id (integer) - the ID of an authorised user
        channel_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the valid user to be invited to the channel
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user already in the channel
        AccessError - Occurs when the authorised user is not a member of the valid channel
    
    Return Value:
        No return value
    """

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
        valid_user_ids.append(user["u_id"])
  
    # Raising an error if u_id is not a valid user 
    # in the created list
    if u_id not in valid_user_ids:
        raise AccessError("Invalid user")
    
    # Raising an error if u_id is already a member of the channel
    channel_count = 0
    for channel in channels:
        if channel_id == channel["channel_id"]:
            break
        channel_count += 1
    members = channels[channel_count]["channel_members"]
    for member in members:
        if u_id == member["u_id"]:
            raise InputError("Already in channel")
    
    # Raising an error if the authorised user 
    # is not a member of the valid channel
    member_of_channel = False
    for member in members:
        if auth_user_id == member["u_id"]:
            member_of_channel = True
    if member_of_channel == False:
        raise AccessError("You are not a member of the channel")

    # Otherwise, add the user to the channel
    
    # Extracting the given user's information
    user_count = 0
    for user in users:
        if user["u_id"] == u_id:
            break
        user_count += 1

    # Appending the user information to the channel
    channels[channel_count]["channel_members"].append(users[user_count])
    
    return {}

def channel_details_v2(token, channel_id):
    """An authorised user to check a channel’s detailed information which user is a member of it
    
    Arguments:
        auth_user_id (integer) - the ID of an authorised user
        channel_id (integer) - the ID of an existing channel

    Exceptions:
        AccessError - Occurs when user type in an invalid id
        AccessError - Occurs when user type in an valid id and valid channel id 
            but user is not a member of that channel
        InputError - Occurs when user type in an invalid channel id

    Return Value:
    {name, is_public, owner_members, all_members }
        name (string) - owner’s first name
        is_public (boolean) - public or private channel
        owner_members(member)
        all_mambers(member)
    {u_id, email, name_first, name_last, handle_str}
        u_id(integer) - the ID of an authorised user
        email (string) - the email of an authorised user
        first name(string) - first name of an authorised user
        last name(string) - last name of an authorised user
        handle_str(string) - special string created for authorised user
    """

    # Obtain data already existed
    data = data_store.get()

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    # Check authorised user is a member of channel or not 
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decode_token['u_id']

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    if check_member(channel_id_element, auth_user_id) == False:
        raise AccessError("Not is not authorised user an member of channel")


    # For return
    channels_details_data = data['channels_details']
    
    name = channels_details_data[channel_id_element]['channel_name']
    owner_members = channels_details_data[channel_id_element]['owner_members']
    all_members = channels_details_data[channel_id_element]['channel_members']
    is_public = channels_details_data[channel_id_element]['channel_status']

    return {
        'name': name,
        'is_public': is_public,
        'owner_members': owner_members,
        'all_members': all_members
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    """The function channel_messages_v1 returns up to 50 messages between the two indexes “start”
    and “start + 50 in a channel of which the authorised user is a member of.”
    
    Arguments:
        auth_user_id (integer) - ID of an authorised user.
        channel_id (integer) - ID of a valid channel.
        start (integer) – the starting index of a list of messages.

    Exceptions:
        InputError – Occurs when 'channel_ID' does not refer to a valid channel
        and the 'start' is greater than the total amount of messages in the channel.
        AccessError – Occurs when the authorised user is not a member of the channel
        and the channel_id is valid.
    
    Return value:
        Returns 'messages' on the condition that the total messages is less than 50.
        Returns 'start' on all conditions.
        Returns 'start + 50' on the condition that total messages is greater than 50.
        Returns 'end' on all conditions.
    """

    # Accessing the data store
    data = data_store.get()

    # create the dictionary messages 
    messages = [ {
        'message_id': '',
        'u_id': '',
        'message': '',
        'time_created': '',
    } ]
    
    # for each channel in channels details 
    for channel in data['channels_details']:
        # add messages dictionary into it 
        channel['messages'] = messages
        channel['start'] = 0
        channel['end'] = 50
        
    # Defining the end index
        end = start + 50
    
    # Creating a list of valid channel IDS
    channels = data["channels_details"]
    valid_channel_ids = []
    for channel in channels:
        valid_channel_ids.append(channel["channel_id"])
    
    # Error raised if the given channel ID is not found in the list
    if channel_id not in valid_channel_ids:
        raise InputError("Invalid channel_id")
   
    # List of valid user IDS
    users = data["users"]
    valid_user_ids = []
    for user in users:
        valid_user_ids.append(user["u_id"])
       
    # Finding the specific channel
    count = 0
    for channel in channels:
        if channel_id == channel["channel_id"]:
            break
        count += 1
       
    # Raising an error if start is greater than
    # the total number of messages in the given channel
    x = channels[count]
    messages = x["messages"]
    print(start)
    print(len(messages))
    if start > len(messages):
        raise InputError("Exceeded total number of messages in this channel")   
       
    # Error if the auth_user is not a member of the valid channel
    members = channels[count]["channel_members"]
    member_of_channel = False
    for member in members:
        if auth_user_id == member["u_id"]:
            member_of_channel = True
    if member_of_channel == False:
        raise AccessError("You are not a member of the channel")

    # Append all messages in a list
    message_list = []
    for message in messages:
        message_list.append(message["message"])
   
    if len(messages) < 50:
        return { 
            'messages': tuple(message_list)[start:end], 
            'start': start,
            'end': -1 
        }
    else:
        return { 
            'messages': tuple(message_list)[start:end], 
            'start': start,
            'end': end 
        }
    

def channel_join_v1(auth_user_id, channel_id):
    """Adding an authorised user to the given valid channel with channel_id
   
    Arguments:
        auth_user_id (integer) - the ID of an authorised user
        channel_id (integer) - the ID of an existing channel
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the authorised user is not a member of the valid channel
        AccessError - Occurs when channel_id is a private channel and the authorised user 
            is not a global owner
    
    Return Value:
        No return value
    """

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
        if auth_user_id == member["u_id"]:
            raise InputError("Already in channel")
    
    # Raising an error if the channel is private
    if channels[channel_count]["channel_status"] != True:
        raise AccessError("Channel is private") 
        
    # Otherwise, add the user to the channel
  
    # Extracting the given user's information
    users = data["users"]
    user_count = 0
    for user in users:
        if user["u_id"] == auth_user_id:
            break
        user_count += 1

    # Appending the user information to the channel
    channels[channel_count]["channel_members"].append(users[user_count])
    
    return {}

def channel_addowner_v1(token, channel_id, u_id):
    data = data_store.get()

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    # Raise a InputError if authorised user type in invalid u_id
    if check_valid_uid(u_id) == False:
        raise InputError("Invalid user ID")

    # Raise a InputError if authorised user type in a valid u_id 
    # but the user with u_id is not a member of channel
    # If the user with u_id is a member of channel then return each_member_id (a list conatins all memebers' u_id)
    each_member_id = check_member(channel_id_element, u_id)
    if each_member_id  == False:
        raise InputError("User is not a member of this channel")
    
    # Obtain a list whcih contains all owners' id
    each_owner_id = channel_owners_ids(channel_id_element)

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is already is an owner of channel
    if u_id in each_owner_id:
        raise InputError("User already is an owner of channel")
    
    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not eligible to add owner
    if check_channel_owner_permissions(token, each_owner_id) == False:
        raise AccessError("No permissions to add user")
    
    # Pick out dict from members and then add it to owner
    new_owner_element = 0
    while new_owner_element < len(each_member_id):
        if u_id == each_member_id[new_owner_element]:
            return new_owner_element
        new_owner_element+= 1
    
    new_owner = data['channels_details'][channel_id_element]['channel_members'][new_owner_element]
    data['channels_details'][channel_id_element]['owner_members'].append(new_owner)

    return {}
    
def channel_removeowner_v1(token, channel_id, u_id):
    data = data_store.get()

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)
    if channel_id_element == False:
        raise InputError("Invalid channel_id")

    # Raise a InputError if authorised user type in invalid u_id
    if check_valid_uid(u_id) == False:
        raise InputError("Invalid user ID")

    # Obtain a list whcih contains all owners' id
    each_owner_id = channel_owners_ids(channel_id_element)

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is not a owner of channel yet
    if u_id not in each_owner_id:
        raise InputError("User is not an owner of channel")

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is only owner of channel
    if u_id in each_owner_id and len(each_owner_id) == 1:
        raise InputError("User is the only owner of channel")

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not eligible to remove owner
    if check_channel_owner_permissions(token, each_owner_id) == False:
        raise AccessError("No permissions to remove user")

    # Pick out dict from owners and then delete it 
    remove_owner_element = 0
    while remove_owner_element < len(each_owner_id):
        if u_id == each_owner_id[remove_owner_element]:
            break
        remove_owner_element += 1

    remove_owner = data['channels_details'][channel_id_element]['owner_members'][remove_owner_element]
    data['channels_details'][channel_id_element]['owner_members'].remove(remove_owner)

    return {}




    