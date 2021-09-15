import time
import zmq
import write_setup
from test_publish_multi_all import Publisher
import health_check

context = zmq.Context()
demosocket = context.socket(zmq.REQ)
demosocket.connect('tcp://127.0.0.1:5560')

def start_objectdemo():
    demosocket.send(b'')
    demosocket.recv()
    print('start objectdemo')

def main(port_number=5000):
    publisher = Publisher()

    #
    while True:
        print('starting flask2 ...')
        write_setup.write_setup_main('config/')
        publisher.run()
        time.sleep(3)
        start_objectdemo()

        while True:
            time.sleep(1000)

        #for i in range(2):
        #    time.sleep(10)
        #    print(f'checking if streams have started ... {i}')
        #    if health_check.run():
        #        print('all out streams started')
        #        break
        #while True:
        #    time.sleep(10)
        #    if not health_check.run():
        #        break
        #    print('all streams are working')


if __name__== "__main__":
    main()
