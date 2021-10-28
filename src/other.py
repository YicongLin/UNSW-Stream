from src.data_store import data_store

def clear_v1():
    """The function clear_v1 resets all the internal data in data_store.py to its initial state.
    There are no paramaters, no exceptions and no returns.
    """
    store = data_store.get()

    store['users'] = []
    store['channels'] = []
    store['channels_details'] = []
    store['emailpw'] = []
    store['dms_details'] = []
    
    data_store.set(store)
    
    return {}

   

    
