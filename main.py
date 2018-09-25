#!/usr/bin/python -u

# Main script for Adafruit Internet of Things Printer 2.  Monitors switch
# for taps and holds, performs periodic actions (Twitter polling by default)
# and daily actions (Sudoku and weather by default).
# Written by Adafruit Industries.  MIT license.
#
# MUST BE RUN AS ROOT (due to GPIO access)
#
# Required software includes Adafruit_Thermal, Python Imaging and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack


#TODO: the printer is really a shared resource and needs to be locked 

from __future__ import print_function
import RPi.GPIO as GPIO
import subprocess, time, socket
from PIL import Image
from Adafruit_Thermal import *
import sys

# ledPin       = 18

switchPin    = 4
holdTime     = 1     # Duration (s) for shutdown
offSwitches    = 3     # Number of swtiches in holdTime to trigger off
nextInterval = 0.0   # Time of next recurring operation
dailyFlag    = False # Set after daily trigger occurs
lastId       = '1'   # State information passed to/from interval script
printer      = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

# Called when switch is briefly tapped.  Invokes time/temperature script.
def tap():
  print("tap")
  subprocess.call(["python", "tap.py"])

# Called when switch is held down.  Prints image, invokes shutdown process.
def hold():
  print("hold")
  subprocess.call("sync")
  subprocess.call("poweroff")

# Called at periodic intervals (30 seconds by default).
# Invokes twitter script.
def interval():
  print("interval")
  p = subprocess.Popen(["python", "interval.py", str(lastId)],
    stdout=subprocess.PIPE)

  return p.communicate()[0] # Script pipes back lastId, returned to main

# Called once per day (6:30am by default).
# Invokes weather forecast and sudoku-gfx scripts.
def daily():
  print("daily")
  subprocess.call(["python", "daily.py"])

# Initialization

# Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setmode(GPIO.BCM)

# Enable swithc (physical pull-up)
GPIO.setup(switchPin, GPIO.IN) 

# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting.
time.sleep(30)

# Show IP address (if network is available)
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 0))
	printer.print('My IP address is ' + s.getsockname()[0])
	printer.feed(3)
except:
	printer.boldOn()
	printer.println('Network is unreachable.')
	printer.boldOff()
	printer.print('Connect display and keyboard\n'
	  'for network troubleshooting.')
	printer.feed(3)
	exit(0)

# Print greeting image
print("started up")
#printer.printImage(Image.open('gfx/hello.png'), True)
#printer.feed(3)

# Poll initial switch state and time
prevSwitchState = GPIO.input(switchPin)
prevTime        = time.time()
numSwitches     = 0    # number of times switch is changed in holdTime

# Main loop
while(True):

  # Poll current switch state and time
  switchState = GPIO.input(switchPin)
  t           = time.time()

  if switchState != prevSwitchState:
    prevSwitchState = switchState
    if numSwitches == 0:
      prevTime = t
    numSwitches = numSwitches + 1

  if (t - prevTime) >= holdTime:
    if numSwitches >= 3:
      hold()
    elif numSwitches == 2:
      pass
    elif numSwitches == 1:
      tap()
    numSwitches = 0
    prevTime = t
  time.sleep(.01) # to debounce

  # Once per day (currently set for 6:30am local time, or when script
  # is first run, if after 6:30am), run daily scripts.
  l = time.localtime()
  if (60 * l.tm_hour + l.tm_min) > (60 * 6 + 30):
    if dailyFlag == False:
      daily()
      dailyFlag = True
  else:
    dailyFlag = False  # Reset daily trigger

  # Every 30 seconds, run interval scripts.  'lastId' is passed around
  # to preserve state between invocations.  Probably simpler to do an
  # import thing.
  if t > nextInterval:
    nextInterval = t + 30.0
    result = interval()
    if result is not None:
      lastId = result.rstrip('\r\n')

