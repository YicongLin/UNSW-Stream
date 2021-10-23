from src.data_store import data_store
from src.error import InputError, AccessError
import hashlib
import jwt

# dm messages function
def dm_messages_v1(token, dm_id, start):
    """The function dm_messages_v1 returns up to 50 messages between the two indexes “start”
    and “start + 50 in a chandmnel of which the authorised user is a member of.”
    
    Arguments:
        token (string) - ID of an authorised user.
        dm_id (integer) - ID of a valid dm.
        start (integer) – the starting index of a list of messages.

    Exceptions:
        InputError – Occurs when 'dm_id' does not refer to a valid dm
        and the 'start' is greater than the total amount of messages in the dm.
        AccessError – Occurs when the authorised user is not a member of the dm
        and the dm_id is valid.
    
    Return value:
        Returns 'messages' on the condition that the total messages is less than 50.
        Returns 'start' on all conditions.
        Returns 'start + 50' on the condition that total messages is greater than 50.
        Returns 'end' on all conditions.
    """

    # Accessing the data store
    data = data_store.get()
    dms = data["dm_details"]

    # create the dictionary messages 
    messages = [ {
        'message_id': '',
        'u_id': '',
        'message': '',
        'time_created': '',
    } ]
    
    # for each dm in dm details 
    for i in range(len(dms)):
        # add messages dictionary into it 
        dms[i]['messages'] = messages
        dms[i]['start'] = 0
        dms[i]['end'] = 50
        
    # Defining the end index
        end = start + 50
    
<<<<<<< HEAD
    # Raising an error if the given dm ID is not 
    # a valid dm in the created list
    is_valid_dm = check_valid_dm_id(dm_id)
    if is_valid_dm == False:
        raise InputError("Invalid dm_id")

=======
    # Creating a list of valid dm IDS
    valid_dm_ids = []
    for i in range(len(dms)):
        valid_dm_ids.append(dms[i]["dm_id"])
    
    # Error raised if the given dm ID is not found in the list
    if dm_id not in valid_dm_ids:
        raise InputError("Invalid dm_id")
   
    # List of valid user IDS
    users = data["users"]
    valid_user_ids = []
    for i in range(len(users)):
        valid_user_ids.append(users[i]["u_id"])
       
    # Finding the specific dm
    count = 0
    for i in range(len(dms)):
        if dm_id == dms[i]["dm_id"]:
            break
        count += 1
       
>>>>>>> master
    # Raising an error if start is greater than
    # the total number of messages in the given dm
    is_greater = start_greater_than_total(dm_id, start)
    if is_greater != False:
        raise InputError("Exceeded total number of messages in this dm") 
        
        
    # Raising an error if the authorised user 
    # is not a member of the valid dm
    SECRET = 'COMP1531'
    decode_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    token = decode_token['u_id']
    
    already_a_member = check_member(dm_id, token)
    if already_a_member == False:
        raise AccessError("You are not a member of the dm")  

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