from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['channel'] = []
    store['channels_details'] = []
    store['channel_id'] = []
    store['channel_status'] = []
    store['members'] = []

    data_store.set(store)
   

    
