from datetime import datetime
import threading

import gmail_util
from util import TOPICS, TIME_FORMAT

class IntervalThread(threading.Thread):
    def __init__(self, printer, printer_lock):
        threading.Thread.__init__(self)
        self.printer = printer
        self.printer_lock = printer_lock

    def run(self):
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
            self.printer_lock.acquire()
            print_message(self.printer, message['Message_body'], message['Sender'])
            self.printer_lock.relase()

def write_new_topic(topic):
    with open(TOPICS, "a") as topics:
        now = datetime.now()
        time_string = now.strftime(TIME_FORMAT)
        topics.write(time_string + "\t" + topic + "\n")

def print_message(printer, body, author):
    printer.setSize('M')
    printer.println("From " + author)

    printer.setSize('S')
    printer.tabwrapOn()
    printer.println(body)
    printer.tabwrapOff()
    printer.feed(1)
