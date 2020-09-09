#!/usr/bin/env python

import os
import time
import sys
import requests
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import AppIot_FleetMgmt as appiot

door_pin = 16
tilt_pin = 13
orange_led_pin = 37
orange_led_state = GPIO.LOW
green_led_pin = 35
# sensor_temp = W1ThermSensor()
sensor_temp = W1ThermSensor()
is_door_open = 0  # False
is_tilted = 0  # False


def post_data(sensor_id, sensor_value, gateway_id):
    #
    # Convert seconds since the Epoch to a date/time: datetime.datetime.fromtimestamp(1172969203)
    # Convert date/time to seconds since the Epoch: now = datetime.datetime.fromtimestamp(1172969203); now.strftime("%s")
    #
    time_now = int(time.time()*1000.0)  # note: need to be in unit of millisecond or second?
    # time_now = int(time.time())  # note: need to be in unit of millisecond or second?
    # print ("time stamp:", time_now)

    sensor_data = '[{"id":"%s","v":[{"m":[%s],"t":%d}]}]' % (sensor_id, sensor_value, time_now)

    headers = { 'Authorization': appiot.httpSAS,
                'DataCollectorId': gateway_id,
                'PayloadType': 'Measurements',
                'Timestamp': time_now,
                'Cache-Control': 'no-cache',
                'Content-Length': len(sensor_data) }
    return(headers,sensor_data)

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
        # select celsius or fahrenheit
        sensor_inputs = { "Temperature":temp_in_celsius, "Is_Open":is_door_open, "Is_Tilted":is_tilted }
        # sensor_inputs = { "Temperature":temp_in_fahrenheit, "Is_Open":is_door_open, "Is_Tilted":is_tilted }

        for sensor_name,sensor_id in appiot.sensors.iteritems():
            # print "Posting: " + sensor_name
            sensor_value = sensor_inputs[sensor_name]
            print "Posting: " + sensor_name + " = " + str(sensor_value)
            (header_data, sensor_data) = post_data(sensor_id, sensor_value, appiot.gateway_id) 
            # print "POSTing... awaiting response."

            response = None

            try:
                response = requests.request('POST', appiot.url, data=sensor_data, headers=header_data, timeout=10)
            except requests.exceptions.RequestException as e:
                print "  ERROR: RequestException: %s" % e
                continue
            finally:
                # print "  WARNING: unexpected condition.  POST may not have been successful."

                if str(response.status_code) != "201":
                    print "  ERROR: Post Response: "+ str(response.status_code) + ": " + response.text
                    # sys.exit(1)
                else:
                    print "Posted %s: %s" % (sensor_name, sensor_data)
                    print "  SUCCESS: Post Status: " + str(response.status_code) + ": " + response.text

        # wait 1 second for each loop
        # time.sleep(5.0)

if __name__ == '__main__': # Program start from here
    setup()
try:
    loop()
except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
    GPIO.cleanup()  # Release resource
    pass
finally:
    GPIO.cleanup()  # Release resource
