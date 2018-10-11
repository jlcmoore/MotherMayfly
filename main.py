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
import threading

# ledPin       = 18
SWITCH_PIN    = 24
HOLD_TIME     = 1     # Duration (s) for shutdown
OFF_SWITCHES    = 3     # Number of swtiches in HOLD_TIME to trigger off

class MainThread (threading.Thread):
  
  def __init__(self):
      threading.Thread.__init__(self)

      self.nextInterval = 0.0   # Time of next recurring operation
      self.dailyFlag    = False # Set after daily trigger occurs
      self.lastId       = '1'   # State information passed to/from interval script
      self.printer      = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

      # Initialization

      # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
      GPIO.setmode(GPIO.BCM)

      # Enable swithc (physical pull-up)
      GPIO.setup(SWITCH_PIN, GPIO.IN) 

      # Processor load is heavy at startup; wait a moment to avoid
      # stalling during greeting.
      time.sleep(30)

      # Show IP address (if network is available)
      try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        self.printer.print('My IP address is ' + s.getsockname()[0])
        self.printer.feed(3)
      except:
        self.printer.boldOn()
        self.printer.println('Network is unreachable.')
        self.printer.boldOff()
        self.printer.print('Connect display and keyboard\n'
          'for network troubleshooting.')
        self.printer.feed(3)
        exit(0)

      # Print greeting image
      print("started up")
  
  def run(self):
    print("Starting Main Thread")
    # Poll initial switch state and time
    prevSwitchState = GPIO.input(SWITCH_PIN)
    prevTime        = time.time()
    numSwitches     = 0    # number of times switch is changed in HOLD_TIME

    # Main loop
    while(True):

      # Poll current switch state and time
      switchState = GPIO.input(SWITCH_PIN)
      t           = time.time()

      if switchState != prevSwitchState:
        prevSwitchState = switchState
        if numSwitches == 0:
          prevTime = t
        numSwitches = numSwitches + 1

      if (t - prevTime) >= HOLD_TIME:
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
        if self.dailyFlag == False:
          daily()
          self.dailyFlag = True
      else:
        self.dailyFlag = False  # Reset daily trigger

      # Every 30 seconds, run interval scripts.  'lastId' is passed around
      # to preserve state between invocations.  Probably simpler to do an
      # import thing.
      if t > self.nextInterval:
        self.nextInterval = t + 30.0
        result = interval(self.lastId)
        if result is not None:
          self.lastId = result.rstrip('\r\n')
    
    print("Ending Main Thread")

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
def interval(lastId):
  print("interval")
  p = subprocess.Popen(["python", "interval.py", str(lastId)],
    stdout=subprocess.PIPE)

  return p.communicate()[0] # Script pipes back lastId, returned to main

# Called once per day (6:30am by default).
# Invokes weather forecast and sudoku-gfx scripts.
def daily():
  print("daily")
  subprocess.call(["python", "daily.py"])

def main():
  main_thread = MainThread()
  main_thread.start()

if __name__ == '__main__':
  main()
