import requests
 

algo_text = [
        'intrusion and loitering',
        'motion detection',
        'vehicle speed and parking',
        'crowd detection',
        'object classification',
        'abandoned object',
        ]

info = [
    ['172.30.1.102',[0,0,0,1,0,1]],
    ['172.30.1.103',[0,0,0,1,0,1]],
    ['172.30.1.23', [0,0,0,1,0,1]],
    ['172.30.1.27', [0,0,0,1,0,1]],
    ['172.30.1.21', [0,0,0,1,0,1]],
    ['172.30.1.20', [0,0,0,1,0,1]],
    ['172.30.5.45', [0,0,0,0,0,1]],
    ['172.30.5.46', [0,0,0,0,0,1]],
    ['172.30.5.47', [0,0,0,1,0,1]],
    ['172.30.5.48', [0,0,0,1,0,1]],
    ['172.30.5.30', [0,0,0,1,0,1]],
    ['172.30.5.32', [0,0,0,1,0,1]],
    #['172.30.1.248',[1,1,1,1,1,1]],
    #['172.30.1.247',[1,1,1,1,1,1]],
    ['172.30.1.93', [1,1,0,1,1,1]],
    ['172.30.1.92', [1,1,0,1,0,0]],
    ['172.30.1.85', [1,1,0,1,0,0]],
    ['172.30.5.36', [1,1,0,1,0,0]],
    ['172.30.5.37', [1,1,0,1,0,0]],
    ['172.30.2.34', [1,1,0,0,0,0]],
    ['172.30.2.35', [1,1,0,0,0,0]],
    ['172.30.2.30', [1,1,0,0,0,0]],
    #['172.30.2.32', [1,1,0,0,0,0]]
    ]

for ip, algos in info:
    for i, run in enumerate(algos):
        if run:
            rtsp = 'rtsp://service:Siemens%23123@{}:554'.format(ip) 
            data = '{},{}'.format(rtsp, algo_text[i])
            requests.post('http://127.0.0.1:5000/', data=data)
            #requests.post('http://127.0.0.1:5000/', data='rtsp://service:Siemens%23123@172.30.2.34:554,object classification')


