# dryot
Dryer IOT Raspberry Pi Project


Copyright and License:
 - The Adafruit.io publishing code is based on the example by Adafruit (c) 2015
 - The dryot sensor code is based on the envirophat motion detection example (c) Pimoroni 2017
 - My original code (if any) and my 3d Design are covered by the MIT license to be compatible with the Adafruit Pimoroni code
 - See the file LICENSE

Installation:
- The python programs in this repository depend on a number of libraries:
  - paho-mqtt python library
```
$ sudo pip3 install paho-mqtt


  - Adafruit IO Python library
```
sudo pip3 install adafruit-io


  - The Pimoroni EnviroPHAT support code and examples:
```
$ curl https://get.pimoroni.com/envirophat | bash


  - Clone this repository
```
$ git clone https://github.com/alanc98/dryot.git


- Make sure you look at the options in the following files:
  - dryot/pi_code/dryot.ini
  - dryot/pi_code/adafruit.io

- Finally, if you want the programs to startup when the Pi boots, add the following to /etc/rc.local
```
python3 /home/pi/dryot/pi_code/dryot_sensor_loop.py &

# Optional, if you want to publish to adafruit.io feeds
python3 /home/pi/dryot/pi_code/dryot_pub_to_adafruit_io.py &


This project is completely documented in a series of YouTube videos:
1. introduction:

