#!/usr/bin/env python3
#  Python script to blink the last octets of the IP address on the activity LED.
#  To be run as root after startup (from crontab, using @reboot)
#
#  Blinks last octet of IP4 address, or last two if second last octet is not 0.
#
#  Each digit is blinked as a roman numberal, with I being a short blink,
#     V a medium blink, and X a long blink.
#
#  For example: 0 is blinked as (X), one long blink, 1 (I) is a short blink,
#     4 (IX) is a short followed by a medium blink
#
#  Install to run at startup with this comment:
#      sudo blink_ip.py install
#
#  Matthias Wandel, August 2020

import sys
import os
import time
import socket
import argparse
import logging as log

ROMANS = ("X", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")

ROMAN_DURATIONS = {
    "I": 0.1,
    "V": 0.4,
    "X": 1.2,
}

DELAY_BETWEEN_ROMAN_DIGITS = 3.0
DELAY_DOT = 1.0

RETURN_CODE_INSTALL_ROOT = 1
RETURN_CODE_ALREADY_INSTALLED = 2


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Blink the IP address on GPIO")
    parser.add_argument("install", help="Install to run at startup", nargs="?")
    parser.add_argument(
            "--log-level", dest="loglevel",
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help="Set the logging level")

    return parser.parse_args()


class LED():
    """
    LED abstraction
    """

    def __init__(self, file="/sys/class/leds/led0/brightness"):
        self.file = open(file, "w")
        self.ON, self.OFF = "1", "0"

        # Activity LED on pi Zero is reverse because it also indicates power
        if not os.path.isdir("/sys/class/leds/led1"):
            log.info("Pi Zero detected")
            self.ON, self.OFF = self.OFF, self.ON

    def set_state(self, state):
        log.debug("setting LED state to %s", state)
        self.file.write(state)
        self.file.flush()

    def blink(self, duration):
        log.debug("blinking LED for %.1fs", duration)
        self.set_state(self.ON)
        time.sleep(duration)

        self.set_state(self.OFF)
        time.sleep(0.2)

    def blink_number_as_roman(self, snum, count=10):
        """
        Takes a number as string and blinks the LED according to its
        roman representation.
        """
        for n in range(count):
            time.sleep(DELAY_BETWEEN_ROMAN_DIGITS)

            for digit in snum:
                if digit == ".":
                    time.sleep(DELAY_DOT)
                    continue

                d = int(digit)
                roman = ROMANS[d]
                log.debug("blinking: %d, %s", d, roman)
                for sym in roman:
                    self.blink(ROMAN_DURATIONS[sym])
                time.sleep(1)


def IPv4_digits(timeout=30):
    """
    Returns up to the last two numbers of the primary IP address
    """

    def IPv4_addr():
        """
        Gets the primary IP address.
        get_ip() from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(("1.2.3.4", 1))  # doesn"t even have to be reachable
                return s.getsockname()[0]
            except socket.gaierror:
                pass

    last_ip, samecount = "", 0

    # Wait up to 30 seconds to get real IP address.
    for n in range(timeout):
        time.sleep(1)

        ip = IPv4_addr()
        log.debug("ip = %s", ip)

        if ip is not None:
            # Sometimes we get a bogus IP address befor valid one.
            if ip == last_ip:
                samecount += 1
                if samecount >= 2:
                    break
            last_ip = ip
        else:
            # Blink three zeros if no real IP address
            ip = "0.000"

    nums = ip.split(".")
    if nums[-2] == "0":
        # Blink last octet only.
        return nums[-1]

    # Blink last two octets
    return ".".join(nums[-2:])


def crontab_install():
    """
    Adds the script to the root user's crontab
    """

    from crontab import CronTab

    try:
        cron = CronTab(user="root")
    except IOError:
        log.error("Superuser privileges required to manipulate root's crontab")
        return RETURN_CODE_INSTALL_ROOT

    # Isolate the script filename
    script_name = os.path.basename(sys.argv[0])

    # Make sure the script is not yet in the crontab
    for job in cron:
        if script_name in job.command:
            log.warning("%s is already on crontab of root", script_name)
            return RETURN_CODE_ALREADY_INSTALLED

    script_dir = os.path.dirname(os.path.realpath(__file__))
    command = os.path.join(script_dir, script_name)

    # Create a new crontab entry
    job = cron.new(command=command)

    # @reboot
    job.every_reboot()

    # Commit the changes
    cron.write()

    log.info("%s added to crontab of user root", script_name)


def main():
    args = parse_args()
    log.debug(args)

    # Log level
    log.root.setLevel(getattr(log, args.loglevel) if args.loglevel else log.INFO)

    # Installation in crontab
    if args.install:
        return crontab_install()

    # Get the last number of the IP address
    iplo = IPv4_digits()

    log.info("Found primary IPv4 address' low digits: %s", iplo)

    # Turn off the LED
    led = LED()
    led.set_state(led.OFF)

    # Blink the number
    led.blink_number_as_roman(iplo)

    # Turn off the LED
    led.set_state(led.OFF)

    # Restore act LED to trigger on file access.
    with open("/sys/class/leds/led0/trigger", "w") as trig:
        trig.write("mmc0")


if __name__ == "__main__":
    sys.exit(main())
