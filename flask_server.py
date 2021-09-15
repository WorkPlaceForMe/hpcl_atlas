import flask
import subprocess
import manage_camDB
import zmq
#import sys
#sys.path.insert(0, "/home/src/final2/analytics")

context = zmq.Context()
demosocket = context.socket(zmq.REQ)
demosocket.connect('tcp://127.0.0.1:5560')

log_dir = '/home/graymatics/dev/atlas/final2/log/'

def start_objectdemo():
    demosocket.send(b'')
    demosocket.recv()
    print('started objectdemo')

def main(port_number=5000):
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True

    @app.route('/restart', methods=['GET'])
    def restart():
        print('restarting flask2')
        subprocess.run('pkill -f flask2.py -9', shell=True)
        subprocess.Popen('python3 flask2.py', shell=True)
        return ''

    @app.route('/', methods=['POST'])
    def start():
        user_data = flask.request.get_data()
        user_rtsp, user_analytic = tuple(user_data.decode().split(','))
        print(f'Camera added {user_rtsp}, {user_analytic}')

        #subprocess.run('rm log/*', shell=True)
        manage_camDB.add(user_rtsp, user_analytic)

        print('restarting flask2')
        subprocess.run('pkill -f flask2.py -9', shell=True)
        #subprocess.run('python3 flask2.py', shell=True)
        subprocess.Popen('python3 flask2.py', shell=True)

        return ''

    @app.route('/remove', methods=['POST'])
    def start_remove():
        user_data = flask.request.get_data()
        user_rtsp, user_analytic = user_data.decode().split(',')
        print(f'Removing {user_rtsp}, {user_analytic}')
        manage_camDB.remove_camera(user_rtsp, user_analytic)

        print('restarting flask2')
        subprocess.run('pkill -f flask2.py -9', shell=True)
        subprocess.Popen('python3 flask2.py', shell=True)
        return ''

    app.run(port=port_number,host='0.0.0.0')


if __name__== "__main__":
    port_number = 5000
    main(port_number)

    # # Run in another script if not working here
    # dummy = subprocess.call(requests.post('http://localhost:{}'.format(port_number), data='rtsp://blah:blah@192.168.1.2'), shell=True)
    # print(dummy.status_code)

