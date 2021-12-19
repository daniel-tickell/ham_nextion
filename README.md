# Raspberry PI Nextion Diplay for mobile Ham Radio operations 

Functions of this code are:
* Display the IP address of the Raspberry pi to the screen
* Display the GPS (Long/Lat/Altitude) as recieved from a USB gps device. 
* Display the CPU Temp in Celsicus
* Display the calculated maidenhead grid reference from the GPS coordinates


Required Packages
*   *sudo apt install python3*
*   *pip3 install [gpsd-py3](https://github.com/MartijnBraam/gpsd-py3)*
*   *pip3 install nextion*
*   *pip3 install maidenhead*

Setup GPSD
*   Connect GPS device and work out which port it is (for me /dev/ttyACM0)
  *   cat /dev/ACM0 and look at the output
*   Edit /etc/default/gpsd to reflect the correct serial port
*   gpsmon should show vaild data   

Setup Nextion
* Wire to the serial Pins on the pi and power as per [this](https://www.f5uii.net/en/tutorial-nextion-screen-on-mmdvm-raspberry-pi/)
* run raspi-config -> interface options -> serial port
* Select No (login Shell) and then Yes (Serial port hardware)

Set to auto Start
* Copy ham_nextion.service to /etc/systemd/system/
* *sudo systemctl daemon-reload*
* *sudo systemctl enable ham_nextion.service*
* *sudo service ham_nextion start*

to check if the service is working
* *sudo service ham_nextion status* 

