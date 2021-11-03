from src.data_store import data_store
import re 
import hashlib
import json

# CODE TO SEND EMAIL 
# https://www.tutorialspoint.com/send-mail-from-your-gmail-account-using-python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_email(receiver_address, contents):
    mail_content = f"This is your password reset code: {contents}"

    # The mail addresses and password
    sender_email = 'camelf15a@gmail.com'
    sender_pass = 'lamepassword'
    receiver_email = receiver_address

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Password reset email'   #The subject line

    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_email, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
    print('Mail Sent')
    
    return {}

# PASSWORD RESET 
def auth_passwordreset_request_v1(email):
    # check valid email - no error if invalid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        return {}

    store = data_store.get()
    print(f"{len(store['emailpw'])}")
    print(f"{len(store['users'])}")

    # check through database 
    i = 0
    while i < len(store['emailpw']):
        # print("oinadjna")
        user = store['emailpw'][i]
        # if registered user:
        if user['email'] == email:
            # print("yayayay")
            # create secret code
            reset_code = hashlib.sha256(email.encode()).hexdigest()
            print(f"{reset_code}")
            # store secret code in emailpw
            user['reset_code'] = reset_code
            # send user an email 
            create_email(email, reset_code)
            # log out of ALL current sessions 
            user['session_id'] = [ ]
            data_store.set(store)
            
        i += 1
    
    # if no matching (unregistered) - no error
    print("+++++++++++")
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()

    # search if email is in datastore 
    i = 0
    while i < len(store['emailpw']):
        user = store['emailpw'][i]
        if user['reset_code'] == hashlib.sha256(reset_code.encode()).hexdigest():
           # remove reset code (one-time use)
           user['reset_code'] = []
           user['password'] = hashlib.sha256(new_password.encode()).hexdigest() 
           data_store.set(store)

        i += 1

    return {}
