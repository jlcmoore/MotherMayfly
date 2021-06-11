#!/usr/bin/python -u

# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

import threading

import poem_utils

class PoemThread(threading.Thread):
    def __init__(self, printer, printer_lock, generate):
        threading.Thread.__init__(self)
        self.printer = printer
        self.printer_lock = printer_lock
        self.generate = generate

    def run(self):
        print("PoemThread run")

        poem = None
        if self.generate:
            poem = poem_utils.get_generated_poem()
        else:
            poem = poem_utils.get_real_poem()

        if poem is None:
            return

        print("PoemThread acquiring lock")
        self.printer_lock.acquire()
        print_poem(self.printer, poem.title, poem.lines, poem.author)

        self.printer.feed(3)
        self.printer.setDefault()
        self.printer_lock.release()

        print("PoemThread run end, released lock")

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
