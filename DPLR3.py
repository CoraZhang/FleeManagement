#!/usr/bin/env python

import os
import time
import sys
import requests
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import AppIot_default as appiot

door_pin = 16
tilt_pin = 13
orange_led_pin = 37
orange_led_state = GPIO.LOW
green_led_pin = 35

sensor_temp = W1ThermSensor()
is_door_open = 0  # False
is_tilted = 0  # False


def post_data(sensor_id, sensor_value, gateway_id):
    
    # TestTruck from the APP IoT 2.0 Gateway ticket.
# Ottawa trailer Lwm2m
    httpSAS = 'SharedAccessSignature sr=https%3a%2f%2fiotabusinesslab.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2fcbb4fa1d-7670-4c57-a94e-e7fb0d1bcfdf%2fmessages&sig=01WDChPcoBfTD3feVYTYtbB%2bgE1RiYZBR376EvDPVEw%3d&se=4696953458&skn=SendAccessPolicy'

    #
    # Get current time in seconds. (works with or without trailing milliseconds)
    time_now = int(time.time())
    #
    # Create http body with sensor data.
    # {
    # "bu":"default-unit",
    # "e":[
    #   {
    #     "n":"[Endpoint]/[ObjectID]/[InstanceID]/[ResourceID]", (TestTruckDevice/3303/0/5700)
    #     "u":"default-unit",
    #     "v":null,   (Numeric Value)
    #     "bv":false, (Boolean Value) 
    #     "sv":null,  (String Value)
    #     "t":1538546399 (Timestamp in Seconds)
    #   }
    #   ]
    # }
    sensor_data = '{"bu":"default-unit","e":[{"n":"%s","u":"default-unit","v":%s,"bv":null,"sv":null,"t":%s}]}' % (sensor_id, sensor_value, time_now)
    #
    # Create headers (http://docs.appiot.io/?page_id=43134)
    headers = { 'Authorization': appiot.httpSAS,
                'DataCollectorId': gateway_id,
                'PayloadType': 'Measurements',
                'Timestamp': time_now,
                'Cache-Control': 'no-cache',
                'Content-Length': len(sensor_data) }

    return(headers,sensor_data)
    # TestTruck Gateway From APP IoT
gateway_id = 'cbb4fa1d-7670-4c57-a94e-e7fb0d1bcfdf'


# APP IoT Mailbox URL for passing in sensor data.
url = 'https://iotabusinesslab.servicebus.windows.net/datacollectoroutbox/publishers/%s/messages' % (gateway_id)

# Sensor that we have defined in APP IoT.

# Associate command-line inputs with target sensor.


for sensor_name,sensor_id in sensors.iteritems():

    sensor_value = sensor_inputs[sensor_name]
    (header_data, sensor_data) = post_data(sensor_id, sensor_value, gateway_id) 
    response = requests.post(url, data=sensor_data, headers = header_data)
    
    if str(response.status_code) != "201":
        print "Error: Post Response: "+ str(response.status_code)
        sys.exit(1)

    print "Posted %s: %s" % (sensor_name, sensor_data)
    print "Post Response Status: " + str(response.status_code)


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(door_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # activate input with PullUp
    GPIO.setup(tilt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(orange_led_pin, GPIO.OUT) # setup pin
    GPIO.output(orange_led_pin, GPIO.HIGH) # light the LED
    GPIO.setup(green_led_pin, GPIO.OUT) # setup pin
    GPIO.output(green_led_pin, GPIO.HIGH) # light the LED

def loop():

    is_door_open = 0  # False
    is_tilted = 0  # False
    orange_led_state = GPIO.HIGH

    while True:
        print time.ctime()
        #temp_in_celsius = 22  # sensor_temp.get_temperature()
        #temp_in_fahrenheit = 79 # sensor_temp.get_temperature(W1ThermSensor.DEGREES_F)
        temp_in_celsius = sensor_temp.get_temperature()
        temp_in_fahrenheit = sensor_temp.get_temperature(W1ThermSensor.DEGREES_F)
        if GPIO.input(door_pin):
            sys.stdout.write("DOOR ALARM: ")
            is_door_open = 1  # True
            GPIO.output(green_led_pin, GPIO.HIGH) # light the green LED
        else:
            sys.stdout.write("DOOR CLOSE: ")
            is_door_open = 0  # False
            GPIO.output(green_led_pin, GPIO.LOW) # turn off the green LED
        #if not GPIO.input(tilt_pin):
	if False:
            sys.stdout.write(" Tilt: ")
            is_tilted = 1  # True
            if orange_led_state == GPIO.HIGH:
                GPIO.output(orange_led_pin, GPIO.LOW)
                orange_led_state = GPIO.LOW
            else:
                GPIO.output(orange_led_pin, GPIO.HIGH)
                orange_led_state = GPIO.HIGH
        else:
            sys.stdout.write(" Flat: ")
            is_tilted = 0  # False
            GPIO.output(orange_led_pin, GPIO.LOW) # turn off the orange LED
            orange_led_state = GPIO.LOW

        sys.stdout.write("Temp ")
        sys.stdout.flush()
        print("{0} C / {1} F".format(temp_in_celsius,temp_in_fahrenheit))

        # Associate command-line inputs with target sensor.
        sensor_inputs = { "Temp_Value_ID":sys.argv[1], "Is_Open_Value_ID":sys.argv[2], "Is_Tilt_Value_ID":sys.argv[3] }
        # select celsius or fahrenheit
        sensors = { "Temp_Value_ID":["41231ece-609a-4a28-8e47-438d7dc7830a","v"], 
            "Is_Open_Value_ID":["d524bb47-4693-4d47-ac06-9343f6615c33","v"],
            "Is_Tilt_Value_ID":["a26227a0-6ed3-4b70-a363-6b247495c0f3","v"] }
            
        sensor_inputs = { "Temp_Value_ID":temp_in_celsius, "Is_Open_Value_ID":is_door_open, "Is_Tilt_Value_ID":is_tilted }
        # sensor_inputs = { "Temperature":temp_in_fahrenheit, "Is_Open":is_door_open, "Is_Tilted":is_tilted }

if len(sys.argv) != 4:
        print "ERROR: Require sensor data to post."
        print "Sensor data order: Temperature is_open is_tilt"
        sys.exit(1)


if __name__ == '__main__': # Program start from here
    setup()
try:
    loop()
except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
    GPIO.cleanup()  # Release resource
    pass
finally:
    GPIO.cleanup()  # Release resource
