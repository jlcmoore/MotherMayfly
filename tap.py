#!/usr/bin/python

# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

from Adafruit_Thermal import *
import Poem

printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

def print_poem(title, lines, author):
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

poem = Poem.generate()
print_poem(poem.title, poem.lines, poem.author)

printer.feed(3)
printer.setDefault()
