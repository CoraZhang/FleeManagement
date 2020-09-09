#!/usr/bin/python

import sys
import json
import requests

# Read in authentication related parameters from JSON config file.
parameters_file = "adal.config.json"

if parameters_file:
    with open(parameters_file, 'r') as f:
        parameters = f.read()
    adal_obj = json.loads(parameters)
else:
    raise ValueError('Please provide parameter file with account information.')

headers = { 'Authorization': adal_obj['AccessToken'],
            'X-DeviceNetwork': adal_obj['deviceNetworkId'],
            'Accept': 'text/plain' }
            
sensors = { "Temp_Value_ID":["41231ece-609a-4a28-8e47-438d7dc7830a","v"], 
            "Is_Open_Value_ID":["d524bb47-4693-4d47-ac06-9343f6615c33","v"],
            "Is_Tilt_Value_ID":["a26227a0-6ed3-4b70-a363-6b247495c0f3","v"] }
# sensors = { "Temp_Value_ID":["41231ece-609a-4a28-8e47-438d7dc7830a","v"] }

for sensor_name,sensor_id in sensors.iteritems():
    url = 'https://lab.api.iot-accelerator.ericsson.net/ddm/api/v3/resources/%s' % (sensor_id[0])
    response = requests.get(url, headers=headers, proxies="")
# print to trouble shoot the python script
    print "%s: " % response.content
    json_response = json.loads(response.content)
    print response.content
    json_LatestMeasurement = json_response.get('LatestMeasurement')

    print "%s: " % (sensor_name)
    if sensor_id[1] == "v":
      print "Name: %s, Values: %s" % (json_response.get("Name"),json_LatestMeasurement.get("v"))
    elif sensor_id[1] == "sv": 
      print "Name: %s, Values: %s" % (json_response.get("Name"),json_LatestMeasurement.get("sv"))
    elif sensor_id[1] == "bv": 
      print "Name: %s, Values: %s" % (json_response.get("Name"),json_LatestMeasurement.get("bv"))
    else:
      print "Name: %s, Values: %s" % (json_response.get("Name"),json_LatestMeasurement.get("v"))
     

