# File: ham_nextion.py
"""
Designed by KM6MZM as a companion screen for a raspberry pi4 with attached Nextion screen

This script is intended to be used to present some basic information about the PI operation and 
GPS data recieved from the Icom IC-705 GPS Serial port on the screen. Additionaly the calculation of
the maiden head grid locator and the ability to touch the status icon to restart gpsd process allows
for ease of setup. 

"""

import time
import socket
import io
import os
import datetime
import maidenhead
import gpsd
import serial.tools.list_ports
import logging
import asyncio
import subprocess

from nextion import Nextion, EventType

#global event_happend


# Check if the GPS is connected & Active
def check_gps():
    try: 
        gpsd.connect()
        current = gpsd.get_current()
        return 1
    except Warning:
        #print("no GPS")
        return 0

#return Longtitude from gpsd
def get_long():
    try: 
        gpsd.connect()
        current = gpsd.get_current()
        gps_lon = current.lon
        return float(gps_lon)
    except Warning:
        return 0

#return Latitude from gpsd
def get_lat():
    try: 
        gpsd.connect()
        current = gpsd.get_current()
        gps_lat = current.lat
        return float(gps_lat)
    except Warning:
        return 0

#return altitude from gpsd
def get_alt():
    try: 
        gpsd.connect()
        current = gpsd.get_current()
        gps_alt = current.alt
        return str(gps_alt)
    except Warning:
        return 0

# take the current GPS coordinates and calculate the maidenhead grid reference
def get_grid():
    current_gps_lat = get_lat()
    current_gps_lon = get_long()
    if current_gps_lat != 0 and current_gps_lon != 0:
        current_grid = maidenhead.to_maiden(current_gps_lat, current_gps_lon)
    else:
        current_grid = "No GPS"
    return current_grid


def get_drift():
    drift_cmd = "chronyc sources | grep NMEA"
    drift_result = str(subprocess.check_output(drift_cmd, shell=True))
    drift = drift_result.split(" ")[0].replace("b'", "")
    return drift
    
#return the current CPU operating temp
def get_cpu_temperature():
    try:
        tFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
        temp = tFile.readline()
        tempC = int(temp)/1000
        return tempC
    except Exception:
        print("failed")

#try to connect to a random IP address in order to determine the working IP 
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Date and Time functions
def get_current_date():
    now = datetime.datetime.now()
    return (now.strftime("%Y-%m-%d"))

def get_current_time():
    now = datetime.datetime.now()
    return (now.strftime("%H:%M"))


# Event handler from Nextion library example - this will listen for touch events
def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    elif type_ == EventType.TOUCH:
        #This will restart gpsd and wait 20 seconds if the status icon on the screen is pressed
        print('Restarting gpsd.service' )
        #os.system("sudo service gpsd restart")
        gps_restart_cmd = "sudo service gpsd restart"
        result = subprocess.check_output(gps_restart_cmd, shell=True)
        #time.sleep(20)
        
async def run():
        # Define the serial paramaters for the Nextion Device
        client = Nextion('/dev/ttyS0', 9600, event_handler)
        await client.connect()
        client.write_command('rest')

        # Check if the gps is working, and set the page/icon accordingly
        while 1: 
            #get_drift() 
            if check_gps() == 1:
                long_status = str(get_long())
                lat_status = str(get_lat())
                alt_status = str(get_alt())
                client.write_command('vis t0,1') # Green Shown 
                client.write_command('vis t10,0')
                client.write_command('vis t11,0')
                next_page = "page 0"

            else:
                long_status =  "--"
                lat_status = "--"
                alt_status = "--"
                next_page = "page 1"
                client.write_command('vis t0,0') # Green Hidden
                client.write_command('vis t10,0') # Yellow Hidden
                client.write_command('vis t11,1') # Red Shown


            
            try:
                await client.set('t3.txt', get_current_time())


                #client.write_command('t3.pco=64388')
                await client.set('t4.txt', get_current_date())

                await client.set('t5.txt', long_status)
                await client.set('t6.txt', lat_status)
                await client.set('t7.txt', "Alt: " + alt_status)

                await client.set('t8.txt', get_grid())
                
                await client.set('t1.txt', get_ip())
                await client.set('t2.txt', " CPU:" + str(get_cpu_temperature()))

            except Exception:
                print( "Exception")

            time.sleep(10)
       
if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.WARNING,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run())
    loop.run_forever()
