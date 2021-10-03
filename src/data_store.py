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
        """ {
            'user_id':1,
            'email' : '34@email.com',
            'password' : 'password', 
            'first_name' : 'name_first', 
            'last_name' : 'name_last'
            
        },

        {
            'user_id': 2
        },

        
        {
            'user_id': 3
        },

        
        {
            'user_id': 4
        } """
    ],
    'emailpw' : [],

    'channels': [
        """ {
            'channel_id': 1,
            'name': 'channel1'
        },

        {
            'channel_id': 2,
            'name': 'channel2'
        },

        {
            'channel_id': 3,
            'name': 'channel3'
        } """
    ],

    'channels_details': [     
            #Input channel_id to track
        """ {
            'channel_id': 1, 
            'channel_statu': True,
            'channels_members': [ 
                {
                    'u_id': 1,
                    'email':'1@email.com', 
                    'name_first':'1first', 
                    'name_last':'1last', 
                    'handle_str': '1str'
                },
                
                {
                    'u_id': 2,
                    'email':'2@email.com', 
                    'name_first':'2first', 
                    'name_last':'2last', 
                    'handle_str': '2str'
                },
            ]
        },

        {
            'channel_id': 2, 
            'channel_statu': True,
            'channels_members': [ 
                {
                    'u_id': 1,
                    'email':'1@email.com', 
                    'name_first':'1first', 
                    'name_last':'1last', 
                    'handle_str': '1str'
                },
                
                {
                    'u_id': 2,
                    'email':'2@email.com', 
                    'name_first':'2first', 
                    'name_last':'2last', 
                    'handle_str': '2str'
                },
            ]
        },

        {
            'channel_id': 3, 
            'channel_statu': True,
            'channels_members': [ 
                {
                    'u_id': 1,
                    'email':'1@email.com', 
                    'name_first':'1first', 
                    'name_last':'1last', 
                    'handle_str': '1str'
                },
                
                {
                    'u_id': 2,
                    'email':'2@email.com', 
                    'name_first':'2first', 
                    'name_last':'2last', 
                    'handle_str': '2str'
                },
            ]
        }, """
        
                    
    ],
    
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

