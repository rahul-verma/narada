import time
import os
from flask import Flask, request, Response
from flask_restful import Api, Resource
from waitress import serve
from uuid import uuid4

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = os.path.join(MY_DIR, "res")

items = []

ditems = dict()

class Item(Resource):

	def __get_item_if_exists(self, name):
		return next(iter(filter(lambda x: x['name'] == name, items)), None)

	def get(self, name):
		item = self.__get_item_if_exists(name)
		return item, item and 200 or 404

	def post(self):
		rdata = request.get_json() #force=True -> now it does not need content-type header
		name = rdata['name']
		item = self.__get_item_if_exists(name)
		if item:
			return {'code' : 'error', 'message' : 'item already exists for name: '  + name}, 400 # Bad Request
		item = {'name' : name, 'price' : rdata['price']}
		items.append(item)
		return {'code' : 'success'}, 200

	def delete(self, name):
		global items
		items = list(filter(lambda x: x['name'] != name, items))
		return {'code' : 'success'}

	def put(self):
		rdata = request.get_json()
		name = rdata['name']
		item = self.__get_item_if_exists(name)
		if item:
			item.update(rdata)
			return {'code' : 'success'}, 200
		else:
			item = {'name' : name, 'price' : rdata['price']}
			items.append(item)
			return {'code' : 'success'}, 201

class DynamicItem(Resource):
    '''
    Generates an ID with post request and get request will work with that ID and not name.
    '''

    def get(self, iid):
        try:
            return ditems[iid], 200
        except KeyError:
            return None, 404

    def post(self):
        rdata = request.get_json() #force=True -> now it does not need content-type header
        iid = str(uuid4())
        rdata["iid"] = iid
        ditems[iid] = rdata
        return ditems[iid], 200

class ItemList(Resource):
	def get(self):
		return {'items' : items}

	def delete(self):
		global items
		items = list()
		return {'code' : 'success'}

class DynamicItemList(Resource):
	def get(self):
		return {'ditems' : ditems}

	def delete(self):
		global ditems
		ditems = dict()
		return {'code' : 'success'}

class Incrementer(Resource):

    def get(self, value):
        return {'value' : value + 1}, 200

class NaradaSvc(Resource):

    def get(self, path):
        f = open(os.path.join(RES_DIR, path), "r")
        res = f.read().replace("${BODY}", "Hello there")
        return Response(res, mimetype="text/html")

def __launch_setu_svc(port):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(NaradaSvc, '/narada', '/narada/<path:path>')
    api.add_resource(Item, '/item', '/item/<string:name>', endpoint='item')
    api.add_resource(ItemList, '/items', endpoint='items')
    api.add_resource(Incrementer, '/inc', '/inc/<int:value>', endpoint='inc')
    api.add_resource(DynamicItem, '/ditem', '/ditem/<string:iid>', endpoint='ditem')
    api.add_resource(DynamicItemList, '/ditems', endpoint='ditems')

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

