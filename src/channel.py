from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import hashlib
import jwt
from src.token_helpers import decode_JWT
from src.users import token_check
from src.message import check_channel, not_a_member, add_notification
from datetime import datetime, timezone

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

    channel_id = int(channel_id)
    channels_details_data = data['channels_details']
    channels_members_element = 0
    all_channel_id = []
    while channels_members_element < len(channels_details_data):
        all_channel_id.append(channels_details_data[channels_members_element]['channel_id'])
        channels_members_element += 1

    channel_id_element = 0
    while channel_id_element < len(all_channel_id):
        if channel_id == all_channel_id[channel_id_element]:
            break
        channel_id_element += 1

    if channel_id not in all_channel_id:
        raise InputError(description="Invalid channel_id")

    return channel_id_element 
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
        raise InputError(description="Invalid uid")

    pass
# Finish valid u_id check
# ==================================

# ==================================
# Check user is a member of channel or not for user
# Serach information at data['channels_details'][channel_id_element]['channel_members']
# If the user with u_id is not a member of channel then return False
# If the user with u_id is a member of channel then return each_member_id (a list conatins all memebers' u_id)
def check_member(channel_id_element, u_id):
    data = data_store.get()

    members_in_channel = data['channels_details'][channel_id_element]['channel_members']
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_channel):
        each_memeber = members_in_channel[each_member_element]
        each_member_id.append(each_memeber['u_id'])
        each_member_element += 1 

    if u_id not in each_member_id:
        raise InputError(description="Authorised user is not a member of this channel")

    return each_member_id
# Finish member users check
# ==================================

# ==================================
# Check user is a member of channel or not for authorised_user
# Serach information at data['channels_details'][channel_id_element]['channel_members']
# If the authorised_user with u_id is not a member of channel then return False
# If the authorised_user with u_id is a member of channel then return each_member_id (a list conatins all memebers' u_id)
def check_member_authorised_user(channel_id_element, token):
    data = data_store.get()

    auth_user_id = decode_JWT(token)['u_id']

    members_in_channel = data['channels_details'][channel_id_element]['channel_members']
    each_member_element = 0
    each_member_id = []
    while each_member_element < len(members_in_channel):
        each_memeber = members_in_channel[each_member_element]
        each_member_id.append(each_memeber['u_id'])
        each_member_element += 1 

    if auth_user_id not in each_member_id:
        raise AccessError(description="User is not a member of this channel")

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

# # ==================================
# # Check token of authorised user is valid or not
# # Search information at data['emailpw']
# # If authorised user with invalid token then return False
# # If authorised user with valid token then return True
def check_valid_token(token):

    store = data_store.get()
    decoded_token = decode_JWT(token)
    
    i = 0
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        # check if session id matches any current session id’s 
        if decoded_token['session_id'] in user['session_id']:
            return 

        i += 1 

    raise AccessError(description = 'Invalid token')

# #Finish authorised user valid token check
# # ==================================

# ==================================
# Check authorised user has channel owner permissions or not
# Search information at each_owner_id(a list contains all owners' u_ids)
# If authorised user has channel/global owener permissions then return False
# If authorised user has channel/global owener permissions then return True
def check_channel_owner_permissions(token, each_owner_id):

    decoded_token = decode_JWT(token)

    owner_permission = decoded_token['permissions_id']
    auth_user_id = decoded_token['u_id']

    if owner_permission != 1 and auth_user_id not in each_owner_id:
        raise AccessError(description="No permissions to add/remove user")

    return True
# Finish authorised user permissions check
# ==================================

# ==================================
# Raising an error if a user is already a member of the channel
def already_a_member(u_id, channel_id):
    data = data_store.get()
    channels = data["channels_details"]
    for i in range(len(channels)):
        if int(channels[i]['channel_id']) == int(channel_id):
            members = channels[i]['channel_members']
            for j in range(len(members)):
                if int(members[j]['u_id']) == int(u_id):
                    raise InputError(description="Already a member of the channel")
# Finish already a member check
# ==================================

# ==================================
# Check whether the start of messages is greater than 
# the total number of messages or not.
# Returns true if start is greater. 
def start_greater_than_total(channel_id, start):
    data = data_store.get()
    channels = data["channels_details"]
    
    for i in range(len(channels)):
        if int(channel_id) == int(channels[i]["channel_id"]):
            x = channels[i]
            messages = x["messages"]
            if int(start) > len(messages):
                raise InputError(description="Exceeded total number of messages in this channel") 
# Finish messages check
# ==================================

# ==================================
# Checking channel status
# Returns false if the channel is private
def channel_status(channel_id):
    data = data_store.get()
    channels = data["channels_details"]
    for i in range(len(channels)):
        if channel_id == channels[i]["channel_id"]:
            if channels[i]["channel_status"] == False:
                raise AccessError(description="Channel is private and you are not a global owner")
# Finish channel status check
# ==================================

# ==================================
# Update timestamps data store whenever a user joins a channel
def timestamps_update_channel_join(auth_user_id):
    data = data_store.get()
    time_joined = int(datetime.now().timestamp())
    users = data['timestamps']['users']

    for i in range(len(users)):
        if users[i]['u_id'] == auth_user_id:
            num_channels_joined = users[i]['channels_joined'][-1]['num_channels_joined'] + 1
            channels_joined_dict = {
                'num_channels_joined': num_channels_joined,
                'time_stamp': time_joined
            }
            users[i]['channels_joined'].append(channels_joined_dict)
    data_store.set(data)

# Finish timestamps data store update
# ==================================

# ==================================
# Update timestamps data store whenever a user leaves a channel
def timestamps_update_channel_leave(auth_user_id):
    data = data_store.get()
    time_left = int(datetime.now().timestamp())
    users = data['timestamps']['users']
    
    for i in range(len(users)):
        if users[i]['u_id'] == auth_user_id:
            num_channels_joined = users[i]['channels_joined'][-1]['num_channels_joined'] - 1
            channels_joined_dict = {
                'num_channels_joined': num_channels_joined,
                'time_stamp': time_left
            }
            users[i]['channels_joined'].append(channels_joined_dict)
    data_store.set(data)
# Finish timestamps data store update
# ==================================

# ==================================
# Update 'channels_joined' when a user joins a channel
def channels_joined_num_join(auth_user_id):
    data = data_store.get()

    # "normal" timestamp for changing number of channels that user is member to
    now_time = datetime.now().timestamp()

    # Pick out user's index in ['timestamps']['users']
    timestamps_user_index = 0
    while True:
        if data['timestamps']['users'][timestamps_user_index]['u_id'] == auth_user_id:
            break
        timestamps_user_index += 1

    # Obtain user's lately channel info
    lately_channels_joined_index = len(data['timestamps']['users'][timestamps_user_index]['channels_joined']) - 1
    lately_channels_joined_num = data['timestamps']['users'][timestamps_user_index]['channels_joined'][lately_channels_joined_index]['num_channels_joined']
    
    # Update channel user's channel info
    new_channels_joined = {
        "num_channels_joined" : (lately_channels_joined_num + 1), 
        "time_stamp" : int(now_time)
    }
    data['timestamps']['users'][timestamps_user_index]['channels_joined'].append(new_channels_joined)

    data_store.set(data)

    pass
# Finish function
# ==================================

# ============================================================
# =====================(Actual functions)=====================
# ============================================================
    
def channel_invite_v2(token, channel_id, u_id):
    """An authorised user who is a member of a channel invites
       another user to join the channel.
   
    Arguments:
        string (integer) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the valid user to be invited to the channel
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user already in the channel
        AccessError - Occurs when the authorised user is not a member of the valid channel
    
    Return Value:
        Empty dictionary on all valid conditions
    """

    # obtaining data
    data = data_store.get()
    channels = data["channels_details"]
    users = data["users"]
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # checks for exceptions
    token_check(token)
    check_channel(channel_id)
    check_valid_uid(u_id) 
    already_a_member(u_id, channel_id)
    not_a_member(auth_user_id, channel_id)

    # otherwise, add the user to the channel
    
    # extracting the given user's index and the authorised user's handle
    for i in range(len(users)):
        if users[i]["u_id"] == u_id:
            user_index = i
        elif users[i]['u_id'] == auth_user_id:
            handle = users[i]['handle_str']
    
    # extracting the given channel's index and name
    for i in range(len(channels)):
        if channels[i]["channel_id"] == int(channel_id):
            channel_index = i
            name = channels[i]["name"]

    # appending the user information to the channel
    channels[channel_index]["channel_members"].append(users[user_index])
    data_store.set(data)

    # adding a notification to the user's notification list
    notification_dict = {
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': f'{handle} added you to {name}'
    }   
    # adding the notification
    add_notification(notification_dict, u_id)

    # updating timestamps store
    timestamps_update_channel_join(u_id)

    return {}

def channel_details_v2(token, channel_id):
    """An authorised user to check a channel’s detailed information which user is a member of it
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user is not a member of that channel
        InputError - Occurs when authorised user type in an invalid channel id

    Return Value:
        {name, is_public, owner_members, all_members}
            name (string) - owner’s first name
            is_public (boolean) - public or private channel
            owner_members (members)
            all_mambers (members)

        members(a list of dict): [{u_id, email, name_first, name_last, handle_str}]
            u_id (integer) - the ID of an authorised user
            email (string) - the email of an authorised user
            first name (string) - first name of an authorised user
            last name (string) - last name of an authorised user
            handle_str (string) - special string created for authorised user
    """

    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    check_member_authorised_user(channel_id_element, token)


    # For return
    channels_details_data = data['channels_details']
    
    name = channels_details_data[channel_id_element]['name']
    owner_members = channels_details_data[channel_id_element]['owner_members']
    all_members = channels_details_data[channel_id_element]['channel_members']
    is_public = channels_details_data[channel_id_element]['channel_status']

    return {
        'name': name,
        'is_public': is_public,
        'owner_members': owner_members,
        'all_members': all_members
    }

def channel_messages_v2(token, channel_id, start):
    """The function channel_messages_v1 returns up to 50 messages between the two indexes “start”
    and “start + 50 in a channel of which the authorised user is a member of.”
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
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

    # obtaining data
    data = data_store.get()
    channels = data["channels_details"]
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # defining the end index
    end = int(start) + 50
    
    # checks for exceptions
    check_valid_channel_id(channel_id)
    token_check(token)        
    start_greater_than_total(channel_id, start)
    not_a_member(auth_user_id, channel_id)

    # finding the channel and accessing messages
    for i in range(len(channels)):
        if int(channels[i]['channel_id']) == int(channel_id):
            channel_messages = channels[i]['messages']

    # append all messages in a list
    message_list = []
    for i in range(len(channels)):
        if int(channels[i]['channel_id']) == int(channel_id):
            channel_messages = channels[i]['messages']
            for j in range(len(channel_messages)):
                message_list.append(channel_messages[j])
    message_list.reverse()

    if len(message_list) < 50:
        return { 
            'messages': message_list[int(start):int(end)], 
            'start': int(start),
            'end': -1 
        }
    else:
        return { 
            'messages': message_list[int(start):int(end)], 
            'start': start,
            'end': end 
        }

def channel_join_v2(token, channel_id):
    """Adding an authorised user to the given valid channel with channel_id
   
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the authorised user is not a member of the valid channel
        AccessError - Occurs when channel_id is a private channel and the authorised user 
            is not a global owner
    
    Return Value:
        Empty dictionary on all valid conditions 
    """

    # obtaining data
    data = data_store.get()
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']
    users = data["users"]
    channels = data["channels_details"]

    # checks for exceptions 
    check_valid_channel_id(channel_id)
    token_check(token) 
    already_a_member(auth_user_id, channel_id)
    if decoded_token['permissions_id'] != 1:
        channel_status(channel_id)
        
    # otherwise, add the user to the channel

    # extracting the given user's index
    for i in range(len(users)):
        if users[i]["u_id"] == auth_user_id:
            user_index = i

    # extracting the given channel's index
    for i in range(len(channels)):
        if channels[i]["channel_id"] == channel_id:
            channel_index = i

    # appending the user information to the channel
    channels[channel_index]["channel_members"].append(users[user_index])
    data_store.set(data)

    # updating timestamps store
    timestamps_update_channel_join(auth_user_id)

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    """An authorised user to add another user as an owner of a channel
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the user who is planned to be added as a new channel owner

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user has not owner permission to add owner
        InputError - Occurs when authorised user type in an invalid channel id
        InputError - Occurs when authorised user type in an invalid u_id
        InputError - Occurs when authorised user type in an valid channel id
            but that user is not a memeber of this channel
        InputError - Occurs when authorised user try to add an existing channel owner as owner

    Return Value:
        {}
    """

    # Obtain data already existed
    data = data_store.get()

    # # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    check_member_authorised_user(channel_id_element, token)

    # Raise a InputError if authorised user type in invalid u_id
    check_valid_uid(u_id)

    # Raise a InputError if authorised user type in a valid u_id 
    # but the user with u_id is not a member of channel
    # If the user with u_id is a member of channel then return each_member_id (a list conatins all memebers' u_id)
    each_member_id = check_member(channel_id_element, u_id)
    
    # Obtain a list whcih contains all owners' id
    each_owner_id = channel_owners_ids(channel_id_element)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not eligible to add owner
    check_channel_owner_permissions(token, each_owner_id)

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is already is an owner of channel
    if u_id in each_owner_id:
        raise InputError(description="User already is an owner of channel")
    
    # Pick out dict from members and then add it to owner
    new_owner_element = 0
    while True:
        if u_id == each_member_id[new_owner_element]:
            break
        new_owner_element+= 1
    
    new_owner = data['channels_details'][channel_id_element]['channel_members'][new_owner_element]
    data['channels_details'][channel_id_element]['owner_members'].append(new_owner)

    return {}
    
def channel_removeowner_v1(token, channel_id, u_id):
    """An authorised user to remove another channel's owner permission
    
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the user who's channel owner permission is planned to be removed

    Exceptions:
        AccessError - Occurs when authorised user with an invalid token
        AccessError - Occurs authorised when user type in an valid id and valid channel id 
            but user has not owner permission to remove owner
        InputError - Occurs when authorised user type in an invalid channel id
        InputError - Occurs when authorised user type in an invalid u_id
        InputError - Occurs when authorised user type in an valid channel id
            but that user is not a existing owner of this channel
        InputError - Occurs when authorised user try to remove the channel owner's owner permission

    Return Value:
        {}
    """
    
    # Obtain data already existed
    data = data_store.get()

    # Raise an AccessError if authorised user login with an invalid token
    check_valid_token(token)

    # Raise a InputError if authorised user type in invalid channel_id
    # If chaneel_id is valid then return channel_id_element (its index at data['channels_details'])
    channel_id_element = check_valid_channel_id(channel_id)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not a member of channel
    check_member_authorised_user(channel_id_element, token)

    # Raise a InputError if authorised user type in invalid u_id
    check_valid_uid(u_id)

    # Obtain a list whcih contains all owners' id
    each_owner_id = channel_owners_ids(channel_id_element)

    # Raise an AccessError if authorised user type in a valid channel_id
    # but the authorised user is not eligible to remove owner
    check_channel_owner_permissions(token, each_owner_id)

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is not a owner of channel yet
    if u_id not in each_owner_id:
        raise InputError(description="User is not an owner of channel")

    # Raise a InputError if authorised user type in a valid u_id
    # but the user with u_id is only owner of channel
    if u_id in each_owner_id and len(each_owner_id) == 1:
        raise InputError(description="User is the only owner of channel")

    # Pick out dict from owners and then delete it 
    remove_owner_element = 0
    while True:
        if u_id == each_owner_id[remove_owner_element]:
            break
        remove_owner_element += 1

    remove_owner = data['channels_details'][channel_id_element]['owner_members'][remove_owner_element]
    data['channels_details'][channel_id_element]['owner_members'].remove(remove_owner)

    return {}

def channel_leave_v1(token, channel_id):
    """An authorised user who is a member of a channel invites
       another user to join the channel.
   
    Arguments:
        token (string) - hashed information of authorised user (including: u_id, session_id, permission_id)
        channel_id (integer) - the ID of an existing channel
       
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when the authorised user is not a member of the valid channel
    
    Return Value:
        Empty dictionary on all valid conditions
    """

    # obtaining data
    data = data_store.get() 
    channels = data["channels_details"]
    decoded_token = decode_JWT(token)
    auth_user_id = decoded_token['u_id']

    # checks for exceptions
    token_check(token)
    check_channel(channel_id)
    not_a_member(auth_user_id, channel_id)
    
    # otherwise, remove the user as a member of the channel
    for i in range(len(channels)):
        if channels[i]["channel_id"] == int(channel_id):
            channel_members = channels[i]["channel_members"]
            owner_members = channels[i]['owner_members']
            # removing the user from the list of members
            for j in range(len(channel_members)):
                if channel_members[j]["u_id"] == auth_user_id: 
                    channel_members.remove(channel_members[j])
                    data_store.set(data)
                    break
            # if necessary, removing the user from the list of owners
            for j in range(len(owner_members)):
                if owner_members[j]['u_id'] == auth_user_id:
                    owner_members.remove(owner_members[j])
                    data_store.set(data)
                    break

    # updating timestamps store
    timestamps_update_channel_leave(auth_user_id)

    return {}
