import hashlib
import json
import jwt

SESSION_TRACKER = 0
SECRET = 'COMP1531'

def generate_new_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

def hash(input_string):    
    return hashlib.sha256(input_string.encode()).hexdigest()

def generate_JWT(u_id, permissions_id, session_id = None):
    if session_id is None:
        session_id = generate_new_session_id()
    return jwt.encode({'u_id' : u_id, 'permissions_id': permissions_id, 'session_id' : session_id}, SECRET, algorithm = 'HS256')     

def decode_JWT(encoded_jwt):
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])

