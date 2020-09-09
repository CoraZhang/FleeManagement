#!/usr/bin/python
'''Return latest sensor data values from AppIoT.'''

import json
import urllib
import requests

import AppIot_default as appiot

# Read in authentication related parameters from JSON config file.
parameters_file = "adal.config.json"

if parameters_file:
    with open(parameters_file, 'r') as f:
        parameters = f.read()
    adal_obj = json.loads(parameters)
else:
    raise ValueError('Please provide parameter file with account information.')

url = "https://login.microsoftonline.com/" + adal_obj['tenantId'] + "/oauth2/token"

params = {"client_id": adal_obj['clientId'],
          "client_secret": adal_obj['clientSecret'],
          "resource": adal_obj['webApiResourceId'],
          "username": adal_obj['username'],
          "password": adal_obj['password'],
          "grant_type": "password",
          'Authorization': adal_obj['AccessToken'],
            'X-DeviceNetwork': adal_obj['deviceNetworkId'],}

headers = {"Cache-Control": "no-cache",
           "Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=urllib.urlencode(params), headers=headers)

#print "Response Status: " + str(response.status_code)

json_data = json.loads(response.text)

accessToken = json_data.get('access_token')

#print "AccessToken: " + accessToken
#print

auth = 'Bearer ' + json_data.get('access_token')

headers = {'Authorization': auth,
           'X-DeviceNetwork': adal_obj['deviceNetworkId'],
           'Content-type': 'application/json'}

sensors = appiot.sensors

for sensor_name, sensor_id in sensors.iteritems():

    url = 'https://eappiot-api.sensbysigma.com/api/v2/sensors/%s/latestmeasurement' % (sensor_id)
    response = requests.get(url, headers=headers)

    print "%s: " % (sensor_name),
    print response.content
