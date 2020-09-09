#!/usr/bin/env python
# Specify setting of AppIoT account and sensors

# From APP IoT 
gateway_id = 'fffb8fc8-6eae-4368-86c2-6eb75c3ff015'
# APP IoT Mailbox URL for passing in sensor data.
url = 'https://eappiotsens.servicebus.windows.net/datacollectoroutbox/publishers/%s/messages' % (gateway_id)
# Sensor that we have defined in APP IoT.
sensors = { "Temperature":"d51d3b56-28e6-48a6-8992-95609d137760",
            "Is_Open":"6e01f16b-f7f7-4fd0-b0e7-3f6c796807ab",
            "Is_Tilted":"e3183f59-4eaa-4523-b0c1-f3b53d3d60a5" }
# From the APP IoT Gateway ticket.
httpSAS = 'SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2ffffb8fc8-6eae-4368-86c2-6eb75c3ff015%2fmessages&sig=jCs12Zn4hYYHZmaPN8wjVLmawTJJnombeD4MKMgQ2X8%3d&se=4632434417&skn=SendAccessPolicy'

