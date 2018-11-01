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

from __future__ import print_function
import socket
import subprocess
import time
import threading
import Queue
import random

from Adafruit_Thermal import Adafruit_Thermal
# from PIL import Image #for graphics
import RPi.GPIO as GPIO

from GracefulKiller import GracefulKiller
import interval
import tap
from util import DEFAULT_TOPICS

DEBOUNCE_TIME = .01
HOLD_TIME = 1     # Duration (s) for shutdown
INIT_SLEEP = 20
INTERVAL_TIME = 5
OFF_SWITCHES = 3     # Number of swtiches in HOLD_TIME to trigger off
PRINTER_LOCATION = "/dev/serial0"
PRINTER_TYPE = 19200
SWITCH_PIN = 24
TOPIC_USES = 3
JOIN_WAIT_TIME = .5

class MainThread(threading.Thread):

    def __init__(self, dead):
        threading.Thread.__init__(self)

        print("MainThread init start")

        self.next_interval = 0.0   # Time of next recurring operation
        self.daily_flag = False # Set after daily trigger occurs
        self.printer = Adafruit_Thermal(PRINTER_LOCATION, PRINTER_TYPE, timeout=5)
        self.printer_lock = threading.Lock()
        self.dead = dead
        self.user_topics = Queue.Queue()
        self.user_topic = None
        self.times_topic_used = 0

        # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
        GPIO.setmode(GPIO.BCM)

        # Enable swithc (physical pull-up)
        GPIO.setup(SWITCH_PIN, GPIO.IN)

        # Processor load is heavy at startup; wait a moment to avoid
        # stalling during greeting.
        time.sleep(INIT_SLEEP)

        # Show IP address (if network is available)
        try:
            self.printer_lock.acquire()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 0))
            self.printer.print('My IP address is ' + sock.getsockname()[0])
            self.printer.feed(3)
        except:
            self.printer.boldOn()
            self.printer.println('Network is unreachable.')
            self.printer.boldOff()
            self.printer.print('Connect display and keyboard\n'
                               'for network troubleshooting.')
            self.printer.feed(3)
            exit(0)
        finally:
            self.printer_lock.release()

        # Print greeting image
        print("MainThread init end")

    def run(self):
        print("Main Thread run")
        # Poll initial switch state and time
        prev_switch_state = GPIO.input(SWITCH_PIN)
        prev_time = time.time()
        num_switches = 0    # number of times switch is changed in HOLD_TIME

        # Main loop
        while not self.dead.is_set():

            # Poll current switch state and time
            switch_state = GPIO.input(SWITCH_PIN)
            now = time.time()

            if switch_state != prev_switch_state:
                prev_switch_state = switch_state
                if num_switches == 0:
                    prev_time = now
                num_switches = num_switches + 1

            if (now - prev_time) >= HOLD_TIME:
                if num_switches >= 3:
                    self.off()
                elif num_switches == 2:
                    self.tap()
                elif num_switches == 1:
                    self.tap(generate=True)
                num_switches = 0
                prev_time = now
            time.sleep(DEBOUNCE_TIME) # to debounce

            # Once per day (currently set for 6:30am local time, or when script
            # is first run, if after 6:30am), run daily scripts.
            local = time.localtime()
            if ((60 * local.tm_hour + local.tm_min) > (60 * 6 + 30) and
                    not self.daily_flag):
                self.daily()
                self.daily_flag = True
            else:
                self.daily_flag = False  # Reset daily trigger

            # Every interval seconds, run interval scripts.
            if now > self.next_interval:
                self.next_interval = now + INTERVAL_TIME
                self.interval()

        print("Main Thread end")

    # Called when switch is briefly tapped.  Invokes time/temperature script.
    def tap(self, generate=False):
        print("tap poem")
        gen_thread = tap.PoemThread(self.printer, self.printer_lock,
                                    self.get_current_topic(), generate)
        gen_thread.start()

    def get_current_topic(self):
        if self.user_topic and self.times_topic_used < TOPIC_USES:
            self.times_topic_used += 1
            return self.user_topic
        self.user_topic = None
        try:
            new_topic = self.user_topics.get_nowait()
            self.times_topic_used = 1
            return new_topic
        except Queue.Empty:
            return random.choice(DEFAULT_TOPICS)

    # Called when switch is held down.  Invokes shutdown process.
    def off(self):
        print("off")
        self.dead.set()
        subprocess.call("sync")
        subprocess.call("poweroff")

    # Called at periodic intervals (30 seconds by default).
    def interval(self):
        print("interval")
        interval_thread = interval.IntervalThread(self.printer, self.printer_lock,
                                                  self.user_topics)
        interval_thread.start()

    def daily(self):
        pass

def main():
    dead = threading.Event()
    killer = GracefulKiller(dead)
    main_thread = MainThread(dead)
    main_thread.start()
    while not dead.is_set():
        main_thread.join(JOIN_WAIT_TIME)

if __name__ == '__main__':
    main()
