import time
import os
from flask import Flask, request, Response
from flask_restful import Api, Resource
from waitress import serve

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = os.path.join(MY_DIR, "res")

class NaradaSvc(Resource):

    def get(self, path):
        f = open(os.path.join(RES_DIR, path), "r")
        res = f.read().replace("${BODY}", "Hello there")
        return Response(res, mimetype="text/html")

def __launch_setu_svc(port):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(NaradaSvc, '/narada', '/narada/<path:path>')

    # api.add_resource(ItemList, '/items', endpoint='items')
    #app.run(port=port, use_evalex=False) #, debug=True)
    serve(app, host="localhost", port=port, _quiet=True)

def wait_for_port(port):
    import socket
    server_address = ('localhost', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ct = time.time()
    while(time.time() - ct < 60):
        try:
            sock.bind(server_address)
            sock.close()
            return
        except Exception as e:
            time.sleep(1)
    print("Port is not open. Timeout after 60 seconds.")
    raise RuntimeError("Another service is running at port {}. Narada could not be launched. Message: ".format(port))

def launch_service(port):
    try:
        wait_for_port(port)
        __launch_setu_svc(port)          
    except Exception as e:
        raise RuntimeError("Not able to launch Narada Service. Got response: ", e)

