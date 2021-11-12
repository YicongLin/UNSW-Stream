import pytest
import requests
import json
from src import config
from src.token_helpers import decode_JWT
from datetime import datetime, timezone
from src.config import url
import os

BASE_URL = url


BROKEN_URL = 'http://asdqwdasfcscd.com'

# Image with width 3958 and height 3030
VALID_JPEG_URL = 'http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg'

# Image with width 159 and height 200
VALID_PNG_URL = 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png'

# ==================================
# Test uploadphoto
# ==================================
def test_uploadphoto():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # user_one 
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})
    decoded_token_1 = decode_JWT(json.loads(response.text)['token'])
    uid_1 = decoded_token_1['u_id']

    # Login in user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Implement uploadphoto(maximum bound) -----> successful implement
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 0, "y_start": 0, "x_end": 3958, "y_end": 3030})
    assert (resp.status_code == 200)

    response = requests.get(f'{BASE_URL}/users/all/v1', params = {"token" : token_1})
    curr_img_url = json.loads(response.text)['users'][0]['profile_img_url'].split("/")
    assert (curr_img_url[len(curr_img_url) - 1] == f'{uid_1}.jpg')

    response = requests.get(f'{BASE_URL}/user/profile/v1', params = {"token" : token_1, "u_id": uid_1})
    curr_img_url = json.loads(response.text)['user']['profile_img_url'].split("/")
    assert (curr_img_url[len(curr_img_url) - 1] == f'{uid_1}.jpg')

    # Implement uploadphoto(normal bound) -----> successful implement
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 150, "y_start": 150, "x_end": 2000, "y_end": 2000})
    assert (resp.status_code == 200)

    response = requests.get(f'{BASE_URL}/users/all/v1', params = {"token" : token_1})
    curr_img_url = json.loads(response.text)['users'][0]['profile_img_url'].split("/")
    assert (curr_img_url[len(curr_img_url) - 1] == f'{uid_1}.jpg')
   
    response = requests.get(f'{BASE_URL}/user/profile/v1', params = {"token" : token_1, "u_id": uid_1})
    curr_img_url = json.loads(response.text)['user']['profile_img_url'].split("/")
    assert (curr_img_url[len(curr_img_url) - 1] == f'{uid_1}.jpg')

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')
    os.unlink(f'/tmp_amd/adams/export/adams/4/z5346398/COMP1531/project-backend/src/static/{uid_1}.jpg')    

def test_uploadphoto_errors():
    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

    # user_one 
    response = requests.post(f'{BASE_URL}/auth/register/v2', json={"email": "testperson@email.com", "password": "password", "name_first": "Test", "name_last": "Person"})

    # Login in user_one
    response = requests.post(f'{BASE_URL}/auth/login/v2', json={"email": "testperson@email.com", "password": "password"})
    token_1 = json.loads(response.text)['token']

    # Implement uploadphoto with a broken URL (InputError 400)
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": BROKEN_URL, "x_start": 10, "y_start": 10, "x_end": 15, "y_end": 15})
    assert (resp.status_code == 400)

    # Implement uploadphoto with a valid .jpg image URL but any image crop bound out of image dimensions (InputError 400)
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": -1, "y_start": 10, "x_end": 15, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 4000, "y_start": 10, "x_end": 4015, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 10, "y_start": -1, "x_end": 15, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": -1, "y_start": 5000, "x_end": 15, "y_end": 5015})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 10, "y_start": 10, "x_end": -15, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 10, "y_start": 10, "x_end": 3959, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 10, "y_start": 10, "x_end": 15, "y_end": 3031})
    assert (resp.status_code == 400)

    # Implement uploadphoto with a valid .jpg image URL but start crop bound less than end's (InputError 400)
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 100, "y_start": 10, "x_end": 15, "y_end": 15})
    assert (resp.status_code == 400)

    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 10, "y_start": 100, "x_end": 4015, "y_end": 15})
    assert (resp.status_code == 400)

    # Implement uploadphoto with a valid .png image URL (InputError 400)
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_PNG_URL, "x_start": 1, "y_start": 1, "x_end": 150, "y_end": 150})
    assert (resp.status_code == 400)

    # Logout user_two
    requests.post(f'{BASE_URL}/auth/logout/v1', json={"token": token_1})

    # User with invalid token to start uploadphoto (AccessError 403)
    # token_2 is invalid already (same token formation)
    resp = requests.post(f'{BASE_URL}/user/profile/uploadphoto/v1', json={"token": token_1, "img_url": VALID_JPEG_URL, "x_start": 1, "y_start": 1, "x_end": 150, "y_end": 150})
    assert (resp.status_code == 403)

    # Clear
    requests.delete(f'{BASE_URL}/clear/v1')

