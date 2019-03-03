# dryot
  # Dryer IOT Raspberry Pi Project

# Copyright and License:
 - The Adafruit.io code is based on the mqtt example by Adafruit (c) 2015
 - The dryot sensor code is based on the envirophat motion detection example (c) Pimoroni 2017
 - My original code and my 3d Design are covered by the MIT license to be compatible with the Adafruit and Pimoroni code
 - See the file LICENSE

# This project is documented in a series of YouTube videos:
1. Project Introduction and Assembly: 

   [![](http://img.youtube.com/vi/7Y_-u9VHjI0/0.jpg)](http://www.youtube.com/watch?v=7Y_-u9VHjI0 "DryOT Project Part 1")


2. Software Setup:

   [![](http://img.youtube.com/vi/UATDyMtNh9s/0.jpg)](http://www.youtube.com/watch?v=UATDyMtNh9s "DryOT Project Part 2")
 
3. Programming: 
   (TBD)
 
# Installation:
1. Install libraries
  - paho-mqtt python library
    ```
    $ sudo pip3 install paho-mqtt
    ```
  - Adafruit IO Python library
    ```
    sudo pip3 install adafruit-io
    ```
  - The Pimoroni EnviroPHAT support code and examples:
    ```
    $ curl https://get.pimoroni.com/envirophat | bash
    ```

2. Clone this repository
    ```
    $ git clone https://github.com/alanc98/dryot.git
    ```
3. Make sure you look at the options in the following files:
    ```
    dryot/pi_code/dryot.ini
    dryot/pi_code/adafruitio.ini
    ```

4. Finally, if you want the programs to startup when the Pi boots, add the following to the bottom of */etc/rc.local*
   ```
   sudo -H -u pi /usr/bin/python3 /home/pi/dryot/pi_code/dryot_sensor_loop.py &

   # Optional, add this if you want to publish to adafruit.io feeds
   sudo -H -u pi /usr/bin/python3 /home/pi/dryot/pi_code/dryot_pub_to_adafruit_io.py &
   ```

