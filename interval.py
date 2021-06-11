import threading

import gmail_util

class IntervalThread(threading.Thread):
    def __init__(self, printer, printer_lock):
        threading.Thread.__init__(self)
        self.printer = printer
        self.printer_lock = printer_lock
        #self.output_poems = output_poems

    def run(self):
        emails = gmail_util.get_new_messages()
        messages = []
        if emails:
            for email in emails:
                if email['Subject'].lower() == 'poem':
                    print("Not Implemented")
                    # will need to call: write_poem(poem, poet_id, cursor):
                    #topic = email['Message_body'].rstrip('\r\n').lower()
                    #self.output_poems.put(topic)
                if email['Subject'].lower() == 'message':
                    messages.append(email)
        for message in messages:
            print("IntervalThread run acquiring lock, has message ", message)
            self.printer_lock.acquire()
            print_message(self.printer, message['Message_body'], message['Sender'])
            self.printer_lock.release()
            print("IntervalThread released lock")

def print_message(printer, body, author):
    printer.setSize('M')
    printer.println("From " + author)

    printer.setSize('S')
    printer.tabwrapOn()
    printer.println(body)
    printer.tabwrapOff()
    printer.feed(3)
