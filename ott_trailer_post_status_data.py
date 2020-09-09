#!/usr/bin/python

import os
import sys
import time
import requests

if len(sys.argv) != 4:
    print "ERROR: Require sensor data to post."
    print "Sensor data order: Temperature is_open is_tilt"
    sys.exit(1)

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
    headers = { 'DataCollectorId': gateway_id,
                'Authorization': httpSAS,
                'PayloadType': 'application/senml+json',
                'Content-Type': 'application/json' }

    return(headers,sensor_data)

###############################################################################

# TestTruck Gateway From APP IoT
gateway_id = 'cbb4fa1d-7670-4c57-a94e-e7fb0d1bcfdf'


# APP IoT Mailbox URL for passing in sensor data.
url = 'https://iotabusinesslab.servicebus.windows.net/datacollectoroutbox/publishers/%s/messages' % (gateway_id)

# Sensor that we have defined in APP IoT.
sensors = { "Temp_Value":"OttawaTruckDeviceType/3303/0/5700", 
            "Is_Open_Value":"OttawaTruckDeviceType/3348/0/5547",
            "Is_Tilt_Value":"OttawaTruckDeviceType/3348/1/5547" }

# Associate command-line inputs with target sensor.
sensor_inputs = { "Temp_Value":sys.argv[1], "Is_Open_Value":sys.argv[2], "Is_Tilt_Value":sys.argv[3] }

for sensor_name,sensor_id in sensors.iteritems():

    sensor_value = sensor_inputs[sensor_name]
    (header_data, sensor_data) = post_data(sensor_id, sensor_value, gateway_id) 
    response = requests.post(url, data=sensor_data, headers=header_data)
    
    if str(response.status_code) != "201":
        print "Error: Post Response: "+ str(response.status_code)
        sys.exit(1)

    print "Posted %s: %s" % (sensor_name, sensor_data)
    print "Post Response Status: " + str(response.status_code)
