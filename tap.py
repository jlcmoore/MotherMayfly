#!/usr/bin/python

# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

from Adafruit_Thermal import *
from poem import Poem
import sys
from util import TOPICS

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
    with open(TOPICS, "r") as f:
        data = f.read()
        last_line = data.readlines()[-1]
        return last_line

def main():
    printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

    topic = read_last_topic()
    # this is very blocking, deal with

    poem = Poem.generate(topic)
    print_poem(printer, poem.title, poem.lines, poem.author)

    printer.feed(3)
    printer.setDefault()

if __name__ == '__main__':
    main()
