import requests
import datetime

timestamp = datetime.datetime.now()

session = requests.Session()

session.auth = ('graymatics', 'Huawei12#$')
url="http://172.30.11.36:9090"
auth = session.post(url)

#headers = {'content-type': 'application/soap+xml'}
def send_milestone(alert, cam_ip):
    headers = {'content-type': 'text/xml'}
    body = """<?xml version="1.0" encoding="utf-8"?>
    <AnalyticsEvent xmlns:i="http://www.w3.org/2001/XMLSchema-instance" 
                    xmlns="urn:milestone-systems">
      <EventHeader>
        <ID>00000000-0000-0000-0000-000000000000</ID>
        <Timestamp>{}</Timestamp>
    
        <Type>MyType</Type>
        
        <!-- Insert Event Message here -->
        <Message>{}</Message>
    
        <Source>
          <!-- Insert camera URI here, if you don't have the GUID. -->
          <!-- (For multichannel devices, URI may contain channel number after ',') -->
          <Name>{},0</Name>
        </Source>
    
      </EventHeader>
    
      <Description>
        Emotion description.
      </Description>
    
      <Location>
        Event location 1
      </Location>
    
      <Vendor>
        <Name>Sam's Vendor</Name>
      </Vendor>
    
    </AnalyticsEvent>""".format(timestamp.strftime("%Y-%m-%dT%H:%M:%S"), alert, cam_ip)
    
    response = session.post(url,data=body,headers=headers)

#print (response.status_code)
#print (response.content)
