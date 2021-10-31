'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [
        
        # {
        #     'u_id': 1,
        #     'email':'1@email.com', 
        #     'name_first': 'a', 
        #     'name_last':'1last', 
        #     'handle_str': 'ahandle1'   
        # },

        # {
        #     'u_id': 2,
        #     'email':'2@email.com', 
        #     'name_first': 'b', 
        #     'name_last':'2last', 
        #     'handle_str': 'bhandle2' 
        # },

        # {
        #     'u_id': 3,
        #     'email':'3@email.com', 
        #     'name_first': 'c', 
        #     'name_last':'3last', 
        #     'handle_str': 'chandle3' 
        # },

        # {
        #     'u_id': 4,
        #     'email':'4@email.com', 
        #     'name_first': 'd', 
        #     'name_last':'4last', 
        #     'handle_str': 'dhandle3' 
        # }
        
    ],
    
    'emailpw' : [
        
        # {
        #     'email' : 'email',
        #     'password' : 'password',
        #     'u_id' : 'new_id',
        #     'permissions_id' : 'permissions_id',
        #     'session_id' : ['session_id']
        # }, 
        
       
    ],

    'dms_details': [
    #  {
    #         'dm_id': 1,
    #         'name': ["ahandle1", "bhandle2", "chandle3"],
    #         'members': [
    #             {
    #                 'u_id': 1,
    #                 'email':'1@email.com', 
    #                 'name_first': 'a', 
    #                 'name_last':'1last', 
    #                 'handle_str': 'ahandle1'
    #             },
    #              {
    #                 'u_id': 2,
    #                 'email':'2@email.com', 
    #                 'name_first': 'b', 
    #                 'name_last':'2last', 
    #                 'handle_str': 'bhandle2'
    #             },
    #             {
    #                 'u_id': 3,
    #                 'email':'3@email.com', 
    #                 'name_first': 'c', 
    #                 'name_last':'3last', 
    #                 'handle_str': 'chandle3'
    #             },
    #         ],
    #         'messages': [
    #             {
    #                 'message_id': 1,
    #                 'u_id': 1,
    #                 'message': 'Hello world',
    #                 'time_created': 1582426789
    #             },
    #         ],
    #         'creator': [
    #             {
    #                 'u_id': 3,
    #                 'email':'3@email.com', 
    #                 'name_first': 'c', 
    #                 'name_last':'3last', 
    #                 'handle_str': 'chandle3'
    #             },
    #         ]
    #     },
    ],

    'channels': [
        # {
        #     'channel_id': 1,
        #     'name': 'channel1'
        # },

        # {
        #     'channel_id': 2,
        #     'name': 'channel2'
        # },

        # {
        #     'channel_id': 3,
        #     'name': 'channel3'
        # } 
    ],

    'channels_details': [     
            #Input channel_id to track
        # {
        #     'name': 'channel1',
        #     'channel_id': 1, 
        #     'channel_status': True,
        #     'owner_members': [
        #         {
        #             'u_id': 1,
        #             'email':'1@email.com', 
        #             'name_first':'1first', 
        #             'name_last':'1last', 
        #             'handle_str': '1str'
        #         },
        #     ],
        #     'channel_members': [ 
        #         {
        #             'u_id': 1,
        #             'email':'1@email.com', 
        #             'name_first':'1first', 
        #             'name_last':'1last', 
        #             'handle_str': '1str'
        #         },
                
        #         {
        #             'u_id': 2,
        #             'email':'2@email.com', 
        #             'name_first':'2first', 
        #             'name_last':'2last', 
        #             'handle_str': '2str'
        #         },
        #     ],
        #     'messages': [
        #         {
        #             'message_id': 1,
        #             'u_id': 1,
        #             'message': 'Hello world',
        #             'time_created': 1582426789,
        #         }
        #     ]             
        # },

        # {
        #     'channel_id': 2, 
        #     'name': 'channel2',
        #     'channel_status': True,
        #     'channel_members': [ 
        #         {
        #             'u_id': 1,
        #             'email':'1@email.com', 
        #             'name_first':'1first', 
        #             'name_last':'1last', 
        #             'handle_str': '1str'
        #         },
                
        #         {
        #             'u_id': 4,
        #             'email':'2@email.com', 
        #             'name_first':'2first', 
        #             'name_last':'2last', 
        #             'handle_str': '2str'
        #         },

        #         {
        #             'u_id': 2,
        #             'email':'2@email.com', 
        #             'name_first':'2first', 
        #             'name_last':'2last', 
        #             'handle_str': '2str'
        #         },
        #     ]
        # },
                       
    ], 
    'deleted_users': [
        # {
        #     'u_id': 1,
        #     'email': '',
        #     'name_first': 'Removed',
        #     'name_last': 'user',
        #     'handle_str': ''
        # }
    ]
 

    

    


}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
