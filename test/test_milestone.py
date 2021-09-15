import sys
sys.path.insert(0, "/home/graymatics/dev/atlas/final2/analytics")
import milestone                                                                                                                    

ms = milestone.Milestone('0.tcp.ap.ngrok.io:164811', 'graymatics', 'graymatics') # 443                                               
ip_sort = ms.ip.split(":")                                                                                                          
event_port = "11224" # 9090                                                                                                         
event_ip = ""                                                                                                                       
client_ip = "192.168.1.0:8090" # actual ip and port on client's vms instance                                                        
for i, replacement in enumerate(ip_sort):                                                                                           
    if i == 1:                                                                                                                      
        replacement = ':' + event_port                                                                                              
    event_ip += replacement  

x1,y1,x2,y2 = 1,1,1,1
ms.send_metadata(event_ip, client_ip, 0, x1, y1, x2, y2)



