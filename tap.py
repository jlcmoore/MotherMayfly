#!/usr/bin/python -u

# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

from datetime import datetime, timedelta
import random
import threading

from poems import Poem
from util import TOPICS, TIME_FORMAT, DEFAULT_TOPICS

TOPIC_LIFE = 3

class TapThread(threading.Thread):
    def __init__(self, printer, printer_lock):
        threading.Thread.__init__(self)
        self.printer = printer
        self.printer_lock = printer_lock

    def run(self):
        print("Starting poem thread")

        topic = read_last_topic()

        # this is very blocking, deal with
        poem = Poem.generate(topic)

        self.printer_lock.acquire()
        print_poem(self.printer, poem.title, poem.lines, poem.author)

        self.printer.feed(3)
        self.printer.setDefault()
        self.printer_lock.release()

def print_poem(printer, title, lines, author):
    printer.underlineOn()
    printer.setSize('M')
    printer.println(title)
    printer.underlineOff()

    printer.setSize('S')
    printer.tabwrapOn()
    for line in lines:
        printer.println(line)
    printer.tabwrapOff()
    printer.feed(1)

    printer.println(author)

def read_last_topic():
    with open(TOPICS, "r") as topics:
        lines = topics.readlines()
        if lines:
            datestr, topic = lines[-1].rstrip().split("\t")
            prev = datetime.strptime(datestr, TIME_FORMAT)
            if datetime.now() - prev < timedelta(minutes=TOPIC_LIFE):
                return topic
        return random.choice(DEFAULT_TOPICS)
