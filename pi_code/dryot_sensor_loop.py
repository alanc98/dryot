#!/usr/bin/env python3
#
# DryOT Envirophat sensor code
# Copyright 2019 Alan Cudmore
# 
# Originally based on the Pimoroni motion_detection.py example
# for the EnviroPHAT. 

import time
from   envirophat import motion, leds, weather, light
import paho.mqtt.client as mqtt

#
# Parameters that can be set in the program
# 
# on_threshold:
#  The number of seconds of detected motion before the program decides that the dryer is on. 
#  Since the dryer will be on for at least 20-30 minutes, it is not unreasonable to make this
#  3 or more seconds. This keeps it from thinking the Dryer is turning on when you are loading
#  it or opening/closing the door. My dryer is not the smoothest, so 3 seems to work fine. 
# 
# off_threshold: 
#  The number of seconds of idle readings before the program decides its off.
#  This will help even out false readings from the accelerometer. If your dryer is very smooth
#  you might need to raise this number. But it's OK if the dryer is on for 30+ minutes.
# 
# threshold:
#  This is the difference between accelerometer readings used to determine if motion has been detected
#  If you want to make this more sensitive for a smoother dryer, you can make this value smaller. 
#  0.005 seems to work well for my dryer, since it is not that smooth. 
#         
# light_threshold:
#   This is the level of light in the room that is used for the light_on/lights_off decision 
#   Anything below this value will be considered "off"
#
on_threshold      = 3
off_threshold     = 3
threshold         = 0.005
light_threshold   = 50 

#
# MQTT Broker address
# 
mqtt_broker_addr = '127.0.0.1'

#
# Parameters you may need to change, but should not have to
# 
samples_per_sec = 4
loop_delay = 0.15

#
# Global variables - Should not have to change any of these
#
state             = 0
threshold_counter = 0
seconds_on        = 0
minutes_on        = 0
hours_on          = 0
saved_seconds_on  = 0
saved_minutes_on  = 0
saved_hours_on    = 0
light_state       = 0

readings          = []
last_z            = 0
motion_detected   = 0

#
# Probably should check to see if these mqtt calls succeed
#
mqtt_client = mqtt.Client("DRYOT")
mqtt_client.connect(mqtt_broker_addr)

try:
    while True:
        start_time = time.time()
        #
        # First, collect samples from the accelerometer
        #  This works well for my dryer, but you might need to change this
        #  if yours is smoother. I have tried it all the way up to 100 samples
        #  per second with no real performance issues. But samples pretty much
        #  work for my dryer. 
        #
        motion_detected = 0
        for x in range (0,samples_per_sec):
           accel_z = motion.accelerometer().z
           # print ('Z = ', accel_z)
           readings.append(accel_z)
           readings = readings[-4:]
           z = sum(readings) / len(readings)
           if last_z > 0 and abs(z-last_z) > threshold:
               motion_detected = 1
               # leds.on()
           last_z = z
           # Make sure this delay matches the number of samples per second
           time.sleep(loop_delay)
           # leds.off()

        #
        # Get light and temperature data
        # 
        light_level = light.light()
        temp = weather.temperature()
 
        #
        # Now that we know if there is motion or not, process the state
        #
        if motion_detected == 1:
           if state == 0:
              #
              # The state is off, and motion was detected
              # so count up on the threshold counter and maybe transition to on
              #
              if threshold_counter < on_threshold:
                 print ('Bump :', threshold_counter )
                 threshold_counter += 1
              else:
                 state = 1
                 threshold_counter = 0
                 print ('state change: From OFF to ON')
           elif state == 1:
              #
              # The state is ON
              # so just keep counting 
              #
              threshold_counter = 0
              seconds_on += 1
              if seconds_on > 59:
                 seconds_on = 0
                 minutes_on += 1
                 if minutes_on > 59:
                    minutes_on = 0
                    hours_on += 1
        else:
           # 
           # Motion detected is false
           #
           if state == 0:
              #
              # only thing to do here is reset any threshold count
              #
              threshold_counter = 0
           elif state == 1:
              # 
              # 
              # 
              if threshold_counter < off_threshold:
                 threshold_counter += 1
                 print ('Pause :', threshold_counter )
                 # 
                 # Keep counting
                 #
                 seconds_on += 1
                 if seconds_on > 59:
                    seconds_on = 0
                    minutes_on += 1
                    if minutes_on > 59:
                       minutes_on = 0
                       hours_on += 1
              else:
                 state = 0
                 threshold_counter = 0
                 saved_seconds_on = seconds_on
                 saved_minutes_on = minutes_on
                 saved_hours_on = hours_on
                 seconds_on = 0
                 minutes_on = 0
                 hours_on = 0
                 print ('state change: From ON to OFF')

        if light_level > light_threshold:
           light_state = 1
        else:
           light_state = 0

        # 
        # Report data to MQTT server
        #
        if state == 0:
           print ('Dryer is OFF')
           mqtt_client.publish('dryot/dryer_state', 'OFF')
        else:
           print ('Dryer is ON')
           mqtt_client.publish('dryot/dryer_state', 'ON')

        previous_dryer_runtime = str(saved_hours_on) + ':' + str(saved_minutes_on) + ':' + str(saved_seconds_on)
        # print('Last Dryer Runtime: ' + previous_dryer_runtime)
        mqtt_client.publish('dryot/previous_dryer_runtime', previous_dryer_runtime)

        dryer_runtime = str(hours_on) + ':' + str(minutes_on) + ':' + str(seconds_on)
        # print('Current Dryer Runtime: ' + dryer_runtime)
        mqtt_client.publish('dryot/dryer_runtime', dryer_runtime)

        # print('Light Level : ', light_level)
        mqtt_client.publish('dryot/light_level', str(light_level))

        if light_state == 0:
           # print ('Lights are OFF')
           mqtt_client.publish('dryot/light_state', 'OFF')
        else:
           # print('lights are ON') 
           mqtt_client.publish('dryot/light_state', 'ON')
        
        mqtt_client.publish('dryot/temperature', '{:.2f}'.format(temp))
        # print('Temperature: %2.3f C' % temp) 

        # 
        # Sleep for the rest of the second
        #
        end_time = time.time() 
        time_diff = end_time - start_time
        time.sleep(time_diff) 
        print ('.')

except KeyboardInterrupt:
    pass