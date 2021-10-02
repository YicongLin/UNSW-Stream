from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['channel'] = []
    store['channel_details'] = []
    return {}
    
    data_store.set(store)
   

    
