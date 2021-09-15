import flask
import random
import time

def get_det():
    det = {}
    det['objID'] = random.randint(0, 7)
    det['pos'] = {}
    det['pos']['ltx'] = x1 = random.randint(0, 1278)
    det['pos']['lty'] = y1 = random.randint(0, 718)
    det['pos']['rbx'] = random.randint(x1, 1279)
    det['pos']['rby'] = random.randint(y1, 719)
    det['conf'] = random.random()
    return det

def get_dets():
    num = random.randint(0, 5)
    dets = []
    for i in range(num):
        dets.append(get_det())
    return dets

def get_all_dets(cam_num):
    msg = ''
    for i in range(cam_num):
        results = {'cam_id':i}
        results['objs'] = get_dets()
        msg += f'&{results}&,'
    msg = msg.replace('\'', '\"').replace(' ', '')
    return msg


def main(port_number=5000):
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True

    @app.route('/', methods=['GET'])
    def start():
        time.sleep(.2)
        return get_all_dets(2)

    app.run(port=port_number)


if __name__== "__main__":
    port_number = 8070
    main(port_number)


