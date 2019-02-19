#!/usr/bin/env python3

#
# Subscribe to MQTT topics and re-publish the data to Adafruit.IO
# Author: Alan Cudmore
# 

#
# This code is based on:
# Example of using the MQTT client class to subscribe to and publish feed values.
# Author: Tony DiCola
# Copyright 2015 Adafruit, see the LICENSE file
#
# MQTT Topics subscribed to:
# 1. dryot/dryer_state --> 'ON' or 'OFF'
# 2. dryot/light_state --> 'ON' or 'OFF'
# 3. dryot/previous_dryer_runtime --> 00:00:00
# 4. dryot/dryer_runtime --> 00:00:00
# 5. dryot/light_level --> 000 representing Lux level
# 6. dryot/temperature --> Temp in Celcius

#
# Adafruit mqtt topics 
# 1. dryot.dryer-state   --> 0 or 1
# 2. dryot.light-state   --> 0 or 1
# 3. dryot.dryer-runtime --> 00:00:00 
# 4. dryot.temperature   --> 00.00 
#

# Import standard python modules.
import random
import sys
import time

# Import Adafruit IO MQTT client.
from   Adafruit_IO import MQTTClient

# Import Paho MQTT client 
import paho.mqtt.client as mqtt

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = 'PUT_YOUR_KEY_HERE'

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'PUT_YOUR_ADAFRUIT_IO_USERNAME_HERE'

# Set to your local MQTT broker address
# if this is running on the RPI Zero, then it can be 
# '127.0.0.1'
mqtt_broker_address = '127.0.0.1'

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

def mqtt_on_message(client, userdata, message):
   #
   # This is the MQTT client message recieive callback
   # Publish selected messages to Adafruit.IO 
   #
   payload_str = message.payload.decode() 
   print (' Payload = ' + payload_str )
   if message.topic == 'dryot/dryer_state':
      if payload_str == 'ON':
         print ('Dryer is ON') 
         aio_client.publish('dryot.dryer-state', '1')
      elif payload_str == 'OFF':
         print ('Dryer is OFF')
         aio_client.publish('dryot.dryer-state', '0')
   elif message.topic == 'dryot/light_state':
      if payload_str == 'ON':
         print ('Light is ON') 
         aio_client.publish('dryot.light-state', '1')
      elif payload_str == 'OFF':
         print ('Light is OFF')
         aio_client.publish('dryot.light-state', '0')
   elif message.topic == 'dryot/dryer_runtime':
      print('Dryer Runtime = ' + payload_str)
      aio_client.publish('dryot.dryer-runtime', payload_str)
   elif message.topic == 'dryot/previous_dryer_runtime':
      print('Previous Dryer Runtime = ' + payload_str)
   elif message.topic == 'dryot/light_level':
      print('Light Level = ' + payload_str)
   elif message.topic == 'dryot/temperature':
      print('Temperature = ' + payload_str)
      aio_client.publish('dryot.temperature', payload_str)
   else:
      print('Unknown message')

   # aio_client.publish(ADAFRUIT_IO_MQTT_TOPIC, value)

# Create an MQTT client instance.
aio_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

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
