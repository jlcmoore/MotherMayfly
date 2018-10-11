#!/usr/bin/python -u

# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

import threading

from poems import Poem

class GeneratePoemThread(threading.Thread):
    def __init__(self, printer, printer_lock, topic):
        threading.Thread.__init__(self)
        self.printer = printer
        self.printer_lock = printer_lock
        self.topic = topic

    def run(self):
        print("Starting poem thread")

        poem = Poem.generate(self.topic)

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
