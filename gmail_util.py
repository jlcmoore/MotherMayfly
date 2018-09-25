'''
	Modified from 'Reading gmail using Python' by Abhishek Chhibber
'''

'''
This script does the following:
- Go to Gmal inbox
- Find and read all the unread messages
- Extract details (Date, Sender, Subject, Snippet, Body) and export them to a .csv file / DB
- Mark the messages as Read - so that they are not read again 
'''

'''
Before running this script, the user should get the authentication by following 
the link: https://developers.google.com/gmail/api/quickstart/python
Also, credentials.json should be saved in the same directory as this file
'''

from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import re
import time
from datetime import datetime
import datetime

USER_ID =  'me'
# Using modify and not readonly, because this will mark the messages Read
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CREDENTIALS = 'credentials.json' 
STORAGE = 'storage.json'

def get_new_messages():
	gmail = auth_gmail()
	unread_msgs = get_unread_msgs_raw(gmail)
	if unread_msgs:
		return parse_messages(unread_msgs, gmail)
	else:
		return None

def auth_gmail():
	# Creating a storage.JSON file with authentication details
	store = file.Storage(STORAGE) 
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets(CREDENTIALS, SCOPES)
	    creds = tools.run_flow(flow, store)
	return discovery.build('gmail', 'v1', http=creds.authorize(Http()))

def get_unread_msgs_raw(gmail):
	label_id_one = 'INBOX'
	label_id_two = 'UNREAD'

	# Getting all the unread messages from Inbox
	# labelIds can be changed accordingly
	unread_msgs = gmail.users().messages().list(userId=USER_ID,labelIds=[label_id_one, label_id_two]).execute()
	# unread_msgs is a dictonary
	messages = None
	num_messages = 0
	if 'messages' in unread_msgs:
		messages = unread_msgs['messages']
		num_messages = str(len(messages))

	return messages

def parse_messages(messages, gmail):
	'''
	The final_list will have dictionary in the following format:

	{	'Sender': '"email.com" <name@email.com>', 
		'Subject': 'Lorem ipsum dolor sit ametLorem ipsum dolor sit amet', 
		'Date': 'yyyy-mm-dd', 
		'Snippet': 'Lorem ipsum dolor sit amet'
		'Message_body': 'Lorem ipsum dolor sit amet'}
	'''
	parsed_messages = [ ]
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

def get_msg(gmail, id):
	return gmail.users().messages().get(userId=USER_ID, id=id).execute() 

def read_msg(gmail, id):
	gmail.users().messages().modify(userId=USER_ID, id=id,body={ 'removeLabelIds': ['UNREAD']}).execute() 

def parse_message(mssg, gmail):
	# fetch the message using API
	message = get_msg(gmail, mssg['id'])
	payload = message['payload']
	header = payload['headers']

	msg_dict = extract_headers(header)
	msg_dict['Snippet'] = message['snippet'] # fetching message snippet

	# Fetching message body
	body_data = payload['body']['data']
	# decoding from Base64 to UTF-8
	#clean_one = body_data.replace("-","+")
	#clean_one = clean_one.replace("_","/")
	decoded_body = base64.b64decode(bytes(body_data), 'UTF-8')

	msg_dict['Message_body'] = decoded_body

	read_msg(gmail, mssg['id'])
	return msg_dict	