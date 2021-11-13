import pickle
import time
from data_store import data_store

def persistence_data():
    # Obtain data already existed
    data = data_store.get()

    with open('database.p', 'wb') as FILE:
        pickle.dump(data, FILE)

    # with open('database.p', 'rb') as FILE:
    #     readable_data = pickle.load(FILE)
    #     print(readable_data)

while True:
    time.sleep(2)
    persistence_data()