'''
    Modified from 'Reading gmail using Python' by Abhishek Chhibber

This script does the following:
- Go to Gmal inbox
- Find and read all the unread messages
- Extract details (Date, Sender, Subject, Snippet, Body) and export them to a .csv file / DB
- Mark the messages as Read - so that they are not read again

Before running this script, the user should get the authentication by following
the link: https://developers.google.com/gmail/api/quickstart/python
Also, credentials.json should be saved in the same directory as this file
'''
import base64

from apiclient import discovery
from httplib2 import Http
import oauth2client

USER_ID =  'me'
# Using modify and not readonly, because this will mark the messages Read
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CREDENTIALS = 'credentials.json'
STORAGE = 'storage.json'

def get_new_messages(unread=True):
    gmail = auth_gmail()
    msgs = get_msgs_raw(gmail, unread)
    if msgs:
        return parse_messages(msgs, gmail)
    return None

def auth_gmail():
    # Creating a storage.JSON file with authentication details
    store = oauth2client.file.Storage(STORAGE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(CREDENTIALS, SCOPES)
        creds = oauth2client.tools.run_flow(flow, store)
    return discovery.build('gmail', 'v1', http=creds.authorize(Http()))

def get_msgs_raw(gmail, unread=True):
    labelIds = ['INBOX']
    if unread:
        labelIds.append('UNREAD')

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    msgs = gmail.users().messages().list(userId=USER_ID,
                                                labelIds=labelIds).execute()
    # msgs is a dictonary
    messages = None
    num_messages = 0
    if 'messages' in msgs:
        messages = msgs['messages']
        num_messages = str(len(messages))

    return messages

def parse_messages(messages, gmail):
    '''
    The final_list will have dictionary in the following format:

    {   'Sender': '"email.com" <name@email.com>',
            'Subject': 'Lorem ipsum dolor sit ametLorem ipsum dolor sit amet',
                'Date': 'yyyy-mm-dd',
                'Snippet': 'Lorem ipsum dolor sit amet'
        'Message_body': 'Lorem ipsum dolor sit amet'}
    '''
    parsed_messages = []
    for mssg in messages:
        message = parse_message(mssg, gmail)
        if message:
            parsed_messages.append(message)
    return parsed_messages

def extract_headers(header):
    msg_dict = {}
    for pair in header:
        name = pair['name']
        value = pair['value']
        if name == 'Subject':
            msg_dict['Subject'] = value
        elif name == 'Date':
            msg_dict['Date'] = str(value)
        elif name == 'From':
            msg_dict['Sender'] = value
    return msg_dict

def get_msg(gmail, mid):
    return gmail.users().messages().get(userId=USER_ID, id=mid).execute()

def read_msg(gmail, mid):
    gmail.users().messages().modify(userId=USER_ID, id=mid,
                                    body={'removeLabelIds': ['UNREAD']}).execute()

def decode(string):
        # decoding from Base64 to UTF-8
    string = string.replace("-", "+")
    string = string.replace("_", "/")
    decoded = base64.urlsafe_b64decode(string.encode('ASCII'))
    return decoded

def parse_message(mssg, gmail):
    # fetch the message using API
    message = get_msg(gmail, mssg['id'])
    payload = message['payload']
    header = payload['headers']

    # Fetching message body
    body = payload['body']

    if not body or 'data' not in body:
        parts = payload['parts']
        if parts and 'body' in parts[0]:
            body = parts[0]['body']
        elif 'parts' in parts and 'body' in parts['parts'][0]:
            body = parts['parts'][0]['body']
        else:
            return None
    if 'data' not in body:
        return None

    body_data = body['data']

    msg_dict = extract_headers(header)
    msg_dict['Snippet'] = message['snippet'] # fetching message snippet

    decoded_body = decode(body_data)

    msg_dict['Message_body'] = decoded_body

    read_msg(gmail, mssg['id'])
    return msg_dict
