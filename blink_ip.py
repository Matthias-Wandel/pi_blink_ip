#!/usr/bin/python3
#  Python script to blink the last octets of the IP address on the activity LED.
#  To be run as root after startup (from crontab, using @reboot)
#

import time, socket, os, sys, subprocess, shutil

#apt-get install python3-pip
#pip3-install python-crontab
from crontab import CronTab

installation_destination = "/root/pi_blink_ip/blink_ip.py"
this_script_location = os.path.abspath(__file__)

#  Blinks last octet of IP4 address, or last two if second last octet is not 0.
#
#  Each digit is blinked as a roman numberal, with I being a short blink,
#     V a medium blink, and X a long blink.
#
romans = ["X","I","II","III","IV","V","VI","VII","VIII","IX"]
#
#  For example: 0 is blinked as (X), one long blink, 1 (I) is a short blink,
#     4 (IV) is a short followed by a medium blink
#
#  Install to run at startup with this comment:
#      sudo blink_ip.py install
#
#  Matthias Wandel, August 2020

if len(sys.argv) == 2:
    if sys.argv[1] != "install":
        print("The only option for this script is 'install'")
        sys.exit()

    # Install blink_ip to run at startup, must run as root.
    user = os.geteuid()
    if user != 0:
        print("You need to be root to install - currently " + user)
        sys.exit()

    try:
        shutil.copyfile (this_script_location, installation_destination)
    except shutil.SameFileError:
        print("Same file detected - skipping : (" + this_script_location + " -> " + installation_destination + ")")
    except Exception as e:
        print(e)
        sys.exit()

    cron = CronTab( user = "root")
    install = False

    if len(cron) == 0:
        print("No jobs installed at all")
        install = True

    jobs = cron.find_command('pi_blink_ip')
    for job in jobs:
        if len(job) > 0:
            print("Job already installed")
            install = False

    if install == True:
        print("Job not found - installing")
        job = cron.new(command = installation_destination)
        job.every_reboot()
        cron.write( user = "root")

def get_ip4_addr():
    # get_ip() from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    # gets the primary IP address.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1)) # doesn't even have to be reachable
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def blink_led(duration):
    ledfile.write(on);
    ledfile.flush()
    time.sleep(duration)
    ledfile.write(off);
    ledfile.flush()
    time.sleep(0.2)

ledfile = open ("/sys/class/leds/led0/brightness","w")
on="1";off="0"
if not os.path.isdir("/sys/class/leds/led1"):
    print("Is pi zero"); # Activity LED on pi zero is backwards because it also indicates power.
    on="0";off="1"

last_ip = ""
samecount = 0
for n in range(30): # Wait up to 30 seconds to get real IP address.
    time.sleep(1)
    ip = get_ip4_addr()
    print("ip =",ip)
    if ip != "127.0.0.1":
        if (ip == last_ip): # Sometimes get a bogus IP address befor real one.
            samecount += 1
            if samecount >= 2: break;
        last_ip = ip
    else:
        ip="0.000" # Blink three zeros if no real IP address

nums = ip.split(".")
if nums[-2] == "0":
    iplo = nums[-1] # Blink last octet only.
else:
    iplo = nums[-2] + "." + nums[-1] # Blink last two octets

blink_led(0)
for n in range(10):
    time.sleep(3)
    for digit in iplo:
        if digit == ".":
            time.sleep(1)
            continue
        roman = romans[eval(digit)]
        print ("blinking ",digit,roman)
        for sym in roman:
            if sym == 'I': blink_led(0.1)
            if sym == 'V': blink_led(0.4)
            if sym == 'X': blink_led(1.2)
        time.sleep(1)
    print()

ledfile.write("0");
ledfile.close()

with open ("/sys/class/leds/led0/trigger","w") as trig:
    trig.write("mmc0") # Restore act LED to trigger on file access.
