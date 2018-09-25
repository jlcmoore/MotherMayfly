import gmail_util
from util import TOPICS
from Adafruit_Thermal import *


def write_new_topic(topic):
	with open(TOPICS, "a") as f:
		f.write(topic + "\n")

def print_message(printer, body, author):
    printer.setSize('M')
    printer.println("From " + author)

    printer.setSize('S')
    printer.tabwrapOn()
    printer.println(body)
    printer.tabwrapOff()
    printer.feed(1)

def main():
	printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)
	#TODO: this is blocking.. need to change?
	emails = gmail_util.get_new_messages()
	messages = []
	if emails:
		for email in emails:
		  if email['Subject'].lower() == 'topic':
		    topic = email['Message_body'].rstrip('\r\n').lower()
		    write_new_topic(topic)
		  if email['Subject'].lower() == 'message':
		  	messages.append(email)
	for message in messages:
		print_message(printer, message['Message_body'], message['Sender'])


if __name__ == '__main__':
	main()