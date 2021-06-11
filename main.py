#!env/bin/python -u

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

from printer import Adafruit_Thermal
# from PIL import Image #for graphics
import RPi.GPIO as GPIO

from GracefulKiller import GracefulKiller
import interval
import poem

DEBOUNCE_TIME = .01
HOLD_TIME = 1     # Duration (s) for shutdown
INIT_SLEEP = 20
INTERVAL_TIME = 5
OFF_SWITCHES = 3     # Number of swtiches in HOLD_TIME to trigger off
PRINTER_LOCATION = "/dev/serial0"
PRINTER_TYPE = 19200
SWITCH_PIN = 24
JOIN_WAIT_TIME = .5

class MainThread(threading.Thread):

    def __init__(self, dead):
        threading.Thread.__init__(self)

        print("MainThread init start")

        self.next_interval = 0.0   # Time of next recurring operation
        self.daily_flag = False # Set after daily trigger occurs
        self.printer = Adafruit_Thermal.Adafruit_Thermal(PRINTER_LOCATION,
                                                         PRINTER_TYPE, timeout=5)
        self.printer_lock = threading.Lock()
        self.dead = dead
        self.network_flag = threading.Event()

        # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
        GPIO.setmode(GPIO.BCM)

        # Enable swithc (physical pull-up)
        GPIO.setup(SWITCH_PIN, GPIO.IN)

        # Processor load is heavy at startup; wait a moment to avoid
        # stalling during greeting.
        time.sleep(INIT_SLEEP)

        with self.printer_lock:
            self.print_startup()
            # Show IP address (if network is available)
            ip_address = getip(self.network_flag)
            if ip_address:
                self.printer.print('Reachable at ' + ip_address)
                self.printer.feed(3)
            self.network_check()

        print("MainThread init end")

    def network_check(self):
        if self.network_flag.is_set():
            self.printer.boldOn()
            self.printer.println('Network is unreachable.')
            self.printer.boldOff()
            self.printer.print('Connect display and keyboard\n'
                               'for network troubleshooting.')
            self.printer.feed(3)
            self.off()

    def print_startup(self):
        self.printer.boldOn()
        self.printer.setSize('L')
        self.printer.println("Mother Mayfly")
        self.printer.boldOff()
        self.printer.setSize('S')
#        self.printer.println("jaredmoore.org/MotherMayfly")
        self.printer.println("Pull cord (three times for help)")

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
                if num_switches >= 4:
                    self.off()
                elif num_switches == 3:
                    self.print_help()
                elif num_switches == 2:
                    self.poem()
                elif num_switches == 1:
                    self.poem(generate=True)
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
    def poem(self, generate=False):
        print("pull poem")
        gen_thread = poem.PoemThread(self.printer, self.printer_lock, generate)
        gen_thread.start()

    def print_help(self):
        with self.printer_lock:
            self.printer.boldOn()
            self.printer.setSize('L')
            self.printer.println("Mother Mayfly")
            self.printer.setSize('S')
            self.printer.println("Jared Moore")
            self.printer.boldOff()
            self.printer.println("2021")
#            self.printer.println("jaredmoore.org/MotherMayfly")
            self.printer.println()

            self.printer.println("Pull the cord")

            self.printer.boldOn()
            self.printer.print("ONCE")
            self.printer.boldOff()
            self.printer.println(" for a computer poem")

            self.printer.boldOn()
            self.printer.print("TWICE")
            self.printer.boldOff()
            self.printer.println(" for a human poem")

            self.printer.boldOn()
            self.printer.print("THRICE")
            self.printer.boldOff()
            self.printer.println(" for this message,")

            self.printer.print("and ")
            self.printer.boldOn()
            self.printer.print(" FOUR")
            self.printer.boldOff()
            self.printer.println(" times to turn it off.")
            self.printer.println()

            self.printer.println("Email")
            self.printer.boldOn()
            self.printer.setSize('M')
            self.printer.println("MotherMayfly@gmail.com")
            self.printer.setSize('S')
            self.printer.boldOff()
            self.printer.println()

            self.printer.println("with a subject of")
            self.printer.boldOn()
            self.printer.setSize('M')
            self.printer.println("message")
            self.printer.setSize('S')
            self.printer.boldOff()
            self.printer.println("to have it print a message.")
            self.printer.println()

            # TODO: the below
            #self.printer.println("with a subject of")
            #self.printer.boldOn()
            #self.printer.setSize('M')
            #self.printer.println("poem")
            #self.printer.setSize('S')
            #self.printer.boldOff()
            #self.printer.println("to set the body of your email")
            #self.printer.println("as a future poem.")

            self.printer.feed(3)

    # Called when switch is held down.  Invokes shutdown process.
    def off(self):
        print("off")
        self.dead.set()
        subprocess.call("sync")
        subprocess.call("reboot")

    # Called at periodic intervals (30 seconds by default).
    def interval(self):
        self.network_check()

        # TODO: save util.py variables

        internet_thread = threading.Thread(target=getip, args=(self.network_flag,))
        internet_thread.start()

        interval_thread = interval.IntervalThread(self.printer, self.printer_lock)
        interval_thread.start()

    def daily(self):
        pass

def getip(flag, host='8.8.8.8', port=0, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((host, port))
        return sock.getsockname()[0]
    except Exception as ex:
        print(ex.message)
        flag.set()

def main():
    dead = threading.Event()
    killer = GracefulKiller(dead)
    main_thread = MainThread(dead)
    main_thread.start()
    while not dead.is_set():
        main_thread.join(JOIN_WAIT_TIME)

if __name__ == '__main__':
    main()
