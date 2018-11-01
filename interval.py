import threading

from gmail import gmail_util

class IntervalThread(threading.Thread):
    def __init__(self, printer, printer_lock, output_topics):
        threading.Thread.__init__(self)
        print("IntervalThread init")
        self.printer = printer
        self.printer_lock = printer_lock
        self.output_topics = output_topics

    def run(self):
        print("IntervalThread run")
        emails = gmail_util.get_new_messages()
        messages = []
        if emails:
            for email in emails:
                if email['Subject'].lower() == 'topic':
                    topic = email['Message_body'].rstrip('\r\n').lower()
                    self.output_topics.put(topic)
                if email['Subject'].lower() == 'message':
                    messages.append(email)
        for message in messages:
            self.printer_lock.acquire()
            print_message(self.printer, message['Message_body'], message['Sender'])
            self.printer_lock.relase()
        print("IntervalThread run done")

def print_message(printer, body, author):
    printer.setSize('M')
    printer.println("From " + author)

    printer.setSize('S')
    printer.tabwrapOn()
    printer.println(body)
    printer.tabwrapOff()
    printer.feed(3)
