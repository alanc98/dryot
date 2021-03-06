#!/usr/bin/env python3

#
# Subscribe to DryOT MQTT topics and re-publish the data to Adafruit.IO
# Author: Alan Cudmore
# 

#
# This code is based on:
# Example of using the MQTT client class to subscribe to and publish feed values.
# Author: Tony DiCola
# Copyright 2015 Adafruit, see the LICENSE file
#
# Subscribe to the following MQTT Topics:
# 1. dryot/dryer_state --> 'ON' or 'OFF'
# 2. dryot/light_state --> 'ON' or 'OFF'
# 3. dryot/previous_dryer_runtime --> 00:00:00
# 4. dryot/dryer_runtime --> 00:00:00
# 5. dryot/light_level --> 000 representing Lux level
# 6. dryot/temperature --> Temp in Celcius

#
# Publish the data to the following Adafruit.io MQTT topics:
# 1. dryot.dryer-state            --> 0 or 1
# 2. dryot.light-state            --> 0 or 1
# 3. dryot.dryer-runtime          --> 00:00:00 
# 4. dryot.temperature            --> 00.00 
# 5. dryot.previous-dryer-runtime --> 00:00:00
# 6. dryot.light-level            --> 000
#

#
# Import standard python modules.
#
import random
import sys
import time

# Import Adafruit IO MQTT client.
from   Adafruit_IO import MQTTClient

# Import Paho MQTT client 
import paho.mqtt.client as mqtt

# Configuration file parser
from configparser import ConfigParser

# Set to your Adafruit IO key and user name.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
adafruit_io_key = 'PUT_YOUR_ADAFRUIT_IO_KEY_HERE'
adafruit_io_username = 'PUT_YOUR_ADAFRUIT_IO_USERNAME_HERE'

# Set to your local MQTT broker address
# if this is running on the RPI Zero, then it can be 
# '127.0.0.1'
mqtt_broker_address = '127.0.0.1'

#
# publish_max sets the number of mqtt packets recieved
# before sending a packet to adafruit.io
publish_max = 12

#
# A set of variables to represent publish rate for each Adafruit.io feed
# The MQTT messages might be too fast for the Adafruit.io feeds, especially if
# on a free account.
# Based on these variables, the every nth message will be sent on to MQTT 
# 
# Seems like a good job for a list of records in python with:
#  - MQTT Topic
#  - Adafruit.io mqtt topic name
#  - Publish rate (max and current)
#  - Type 
#
# But for now, the compromise is the hard coded variables
#

_dryer_state_count = 0
_light_state_count = 0
_dryer_runtime_count = 0
_dryer_prev_runtime_count = 0
_temperature_count = 0
_light_level_count = 0

#####################################################################
#
parser = ConfigParser()
parser.read('/home/pi/dryot/pi_code/adafruitio.ini')

if parser.has_section('adafruitio') == True:
    if parser.has_option('adafruitio', 'adafruit_io_key') == True:
        adafruit_io_key =  parser.get('adafruitio', 'adafruit_io_key')

    if parser.has_option('adafruitio', 'adafruit_io_username') == True:
        adafruit_io_username =  parser.get('adafruitio', 'adafruit_io_username')

    if parser.has_option('adafruitio', 'publish_max') == True:
        publish_max =  parser.getint('adafruitio', 'publish_max')

if parser.has_section('mqtt') == True:
    if parser.has_option('mqtt', 'mqtt_broker_addr') == True:
        mqtt_broker_addr = parser.get('mqtt', 'mqtt_broker_addr')

# Define callback functions which will be called when certain events happen.
def aio_connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!')

def aio_disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def aio_message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    # This is not that important, since we are not subscribing to Adafruit IO feeds for this 
    # project.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

#
# Most of the work is done in the on_message function
# The function is called when an MQTT message is received
#
def mqtt_on_message(client, userdata, message):
   global publish_max
   global _dryer_state_count
   global _light_state_count
   global _dryer_runtime_count
   global _dryer_prev_runtime_count
   global _temperature_count
   global _light_level_count

   #
   # This is the MQTT client message recieive callback
   # Re-publish selected messages to Adafruit.IO
   # There is also code to control the rate that the messages
   # are re-published to Adafruit.io.
   # For each topic, a counter is kept, so only the nth
   #  message is sent.
   #
   payload_str = message.payload.decode() 
   # print (' Payload = ' + payload_str )
   if message.topic == 'dryot/dryer_state':
      if _dryer_state_count == publish_max:
         _dryer_state_count = 0
         if payload_str == 'ON':
            # print ('Dryer is ON') 
            aio_client.publish('dryot.dryer-state', '1')
         elif payload_str == 'OFF':
            # print ('Dryer is OFF')
            aio_client.publish('dryot.dryer-state', '0')
      else:
         _dryer_state_count += 1 
   elif message.topic == 'dryot/light_state':
      if _light_state_count == publish_max:
         _light_state_count = 0
         if payload_str == 'ON':
            # print ('Light is ON') 
            aio_client.publish('dryot.light-state', '1')
         elif payload_str == 'OFF':
            # print ('Light is OFF')
            aio_client.publish('dryot.light-state', '0')
      else:
         _light_state_count += 1 
   elif message.topic == 'dryot/dryer_runtime':
      if _dryer_runtime_count == publish_max:
         _dryer_runtime_count = 0
         # print('Dryer Runtime = ' + payload_str)
         aio_client.publish('dryot.dryer-runtime', payload_str)
      else:
         _dryer_runtime_count += 1
   elif message.topic == 'dryot/previous_dryer_runtime':
      if _dryer_prev_runtime_count == publish_max:
         _dryer_prev_runtime_count = 0
         # print('Previous Dryer Runtime = ' + payload_str)
         aio_client.publish('dryot.previous-dryer-runtime', payload_str)
      else:
         _dryer_prev_runtime_count += 1
   elif message.topic == 'dryot/light_level':
      if _light_level_count == publish_max:
         _light_level_count = 0
         # print('Light Level = ' + payload_str)
         aio_client.publish('dryot.light-level', payload_str)
      else:
         _light_level_count += 1
   elif message.topic == 'dryot/temperature':
      if _temperature_count == publish_max:
         _temperature_count = 0
         # print('Temperature = ' + payload_str)
         aio_client.publish('dryot.temperature', payload_str)
      else:
         _temperature_count += 1
   else:
      print('Unknown message')

# Create an MQTT client instance.
aio_client = MQTTClient(adafruit_io_username, adafruit_io_key)

# Setup the callback functions defined above.
aio_client.on_connect    = aio_connected
aio_client.on_disconnect = aio_disconnected
aio_client.on_message    = aio_message

# Connect to the Adafruit IO server.
aio_client.connect()

# Use a client loop function to ensure messages are doing things in the program 
# In this case we need to subscribe to local MQTT topics and receive data from them
aio_client.loop_background()

# connect to the Mosquitto MQTT broker 
mqtt_client = mqtt.Client("DRYOT2AIO")
mqtt_client.on_message = mqtt_on_message
mqtt_client.connect(mqtt_broker_address)

# Start the mqtt client thread
mqtt_client.loop_start()

#
# Subscribe to the MQTT topics for the DryOT project
#
mqtt_client.subscribe('dryot/dryer_state')
mqtt_client.subscribe('dryot/light_state')
mqtt_client.subscribe('dryot/dryer_runtime')
mqtt_client.subscribe('dryot/previous_dryer_runtime')
mqtt_client.subscribe('dryot/light_level')
mqtt_client.subscribe('dryot/temperature')

#
# Main loop will just sit idle
# The work is being done mostly in the MQTT client loop
#
try:
   while True:
      time.sleep(5)

except KeyboardInterrupt:
   mqtt_client.loop_stop()
   pass 
