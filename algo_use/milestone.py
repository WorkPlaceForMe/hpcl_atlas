import uuid
import base64
import re
import requests
import datetime


class Milestone:
    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def get_url(self):
        url = 'https://{}/ManagementServer/ServerCommandService.svc'.format(self.ip)
        return url
    
    def get_data(self):
        body = '''<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <Login xmlns="http://videoos.net/2/XProtectCSServerCommand">
                            <instanceId>{} </instanceId>
                            <currentToken></currentToken>
                        </Login>
                    </soap:Body>
            </soap:Envelope>
            '''.format(uuid.uuid4())
        return body

    def get_headers(self):
        headers = {
            'Content-Type':'text/xml; charset=utf-8',
            'SOAPAction':'http://videoos.net/2/XProtectCSServerCommand/IServerCommandService/Login',
            'Connection':'close'
        }
        headers['Host'] = self.ip
        headers['Authorization'] = self.get_auth(self.user, self.passwd)
        return headers

    @staticmethod
    def get_auth(user, passwd):
        message = "[BASIC]\\{}:{}".format(user, passwd)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return 'Basic ' + base64_message
    
    @staticmethod
    def extract_token(response): 
        response = str(response.content)
        token = re.search('<Token>(.*)</Token>', response).group(1)
        return token

    def send_alarm(self, event, client, camera_index, data):
        try:
            timestamp = datetime.datetime.now()
            session = requests.Session()
            session.auth = (self.user, self.passwd)
            # url = f'http://{self.ip}:{port}'
            url = 'http://{}'.format(event)
            auth = session.post(url)
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
            <AnalyticsEvent xmlns:i="http://www.w3.org/2001/XMLSchema-instance" 
                            xmlns="urn:milestone-systems">
            <EventHeader>
                <ID>00000000-0000-0000-0000-000000000000</ID>
                <Timestamp>{}</Timestamp>

                <Type>MyType</Type>
                
                <!-- Insert Event Message here -->
                <Message>Face Recognition</Message>

                <Source>
                <!-- Insert camera URI here, if you don't have the GUID. -->
                <!-- (For multichannel devices, URI may contain channel number after ',') -->
                <Name>{}</Name>
                </Source>

            </EventHeader>

            <Description>{}                                                                                   </Description>

            <Location>
                Event location 1
            </Location>

            <Vendor>
                <Name>The Vendor's name</Name>
            </Vendor>

            </AnalyticsEvent>""".format(timestamp.strftime("%Y-%m-%dT%H:%M:%S"), client + ',{}'.format(camera_index), data)

            response = session.post(url,data=body,headers=headers)
        except:
            pass

        # print (response.status_code)
        # print (response.content)

    def send_metadata(self, event, client, camera_index, x1, y1, x2, y2):
        try:
            timestamp = datetime.datetime.now()
            session = requests.Session()
            session.auth = (self.user, self.passwd)
            x1 = x1/1280
            y1 = y1/720
            x2 = x2/1280
            y2 = y2/720
            # url = f'http://{self.ip}:{port}'
            url = 'http://{}'.format(event)
            auth = session.post(url)
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
            <AnalyticsEvent xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:milestone-systems">
                <EventHeader>
                    <ID>00000000-0000-0000-0000-000000000000</ID>
                    <Timestamp>{}</Timestamp>
                    <Message>Bounding Box</Message>

                    <Source>
                        <Name>{}</Name>
                    </Source>

                </EventHeader>

                <ObjectList>
                    <Object>
                        <BoundingBox>
                            <Top>{}</Top>
                            <Left>{}</Left>
                            <Bottom>{}</Bottom>
                            <Right>{}</Right>
                        </BoundingBox>
                    </Object>
                </ObjectList>
            </AnalyticsEvent>""".format(timestamp.strftime("%Y-%m-%dT%H:%M:%S"), client + ',{}'.format(camera_index), y1, x1, y2, x2)
            print("y1: ", y1)
            print("x1: ", x1)
            print("y2: ", y2)
            print("x2: ", x2)

            response = session.post(url,data=body,headers=headers)

            print (response.status_code)
            print (response.content)
        except:
            pass

    # def live(self):
    #     global live_request_id 
    #     live_request_id = 0
    #     global s2 
        
    #     data5 = f"<?xml version='1.0' encoding='UTF-8'?><methodcall><requestid>{live_request_id}</requestid><methodname>live</methodname></methodcall>".format(live_request_id=live_request_id) + "\r\n\r\n" 
    #     data5_bytes = bytes(data5, encoding="UTF-8", errors="replace") 
    #     s2.sendall(data5_bytes) 
    #     live_request_id = live_request_id + 1 
            
    #     while True: 
    #         data = b'' 
    #         respHeader = recvall(s2, data, 4096) 
    #         #print(respHeader.decode('utf-8', 'replace')) 
    #         #print(respHeader) 
    #         respArray = respHeader.split(b'\r\n\r\n') 
    #         if respArray[0].startswith(b'ImageResponse'): 
    #             head = respArray[0] 
    #             body = respArray[1] 
    #             #print(body) 
    #             arr = bytearray(body) 
    #             # print((arr[32:])) 
    #             # print(head) 
    #             # print(body)

def login3():
    ms = Milestone('192.168.1.0', 'graymatics', 'graymatics')
    response = requests.post(url=ms.get_url(), headers=ms.get_headers(), data=ms.get_data(), verify=False)
    print(response.content)
    token = ms.extract_token(response)
    print(token)

if __name__=='__main__':
    login3()
    
