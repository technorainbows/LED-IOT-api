#!/usr/bin/env python
from flask_cors import CORS
from flask import Flask, jsonify, request, json
from flask_restplus import Api, Resource, fields, cors
# from werkzeug.contrib.fixers import ProxyFix
import redis
import json

app = Flask(__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='0.2', title='LED API',
    description='A simple LED IOT API', doc='/docs'
)

CORS(app)
# ns = api.namespace('Devices', description='DEVICES operations')

'''Initial dictionary of devices '''
DEVICES = {
    'device1': 
        {
            'onState': 'False', 
            'brightness': 200,
            'name':'Ashley-Triangle'
        },
    'device2': 
        {
            'onState': 'True', 
            'brightness': 100,
            'name':'Other'
        }
}




'''Single Device Data Model'''
device = api.model('Device', {
    'onState': fields.Boolean(description='The on/off state', attribute='onState', required=False, default=True),
    'brightness': fields.Integer(description='The LED brightness', attribute='brightness', min=0, max=255, required=False, default=255),
    'name': fields.String(description="name of the device", attribute='name', required=False, default='N/A')
})

'''Device List Data Model'''
list_of_devices = api.model('ListedDevices', {
    'id': fields.String(required=True, description='The device ID'),
    'device': fields.Nested(device, description='The device')
})


def abort_if_device_not_found(device_id):
    if device_id not in DEVICES:
        api.abort(404, "Device {} doesn't exist".format(device_id))



# ''''''''''''
# '''REDIS''''
# ''''''''''''


# r.hmset('device1',DEVICES['device1'])
# r.hmset('device2',DEVICES['device2'])r =

# rDevices1 = r.hgetall('device1')
# print('rDevice1s: ', rDevices1)
# rDevices2 = r.hgetall('device2')
# print('rDevice2s: ', rDevices2)



# print(r.hgetall('device1'))
# print(r.hgetall('device2'))

# '''Initial Write of DEVICES data to REDIS'''
# with r.pipeline() as pipe:
#     for device_id, device in DEVICES.items():
#         pipe.hmset(device_id,device)
#     pipe.execute()
# r.bgsave()

# LUA_HMGET =  """
#     if redis.call('EXISTS', KEYS[1]) == 1 then
#         return redis.call('HGETALL', KEYS[1])
#     else
#         redis.call('HMSET', KEYS[1], ARGV[1] ARGV[2])
#         return ARGV[2]
#     end
#     """

'''
lua script gets device settings from Redis if there, otherwise 
initializes device settings to default
'''

LUA_GET =  """
    if redis.call('EXISTS', KEYS[1]) == 1 then
        return redis.call('GET', KEYS[1])
    else
        redis.call('SET', KEYS[1], ARGV[1])
        return ARGV[1]
    end
    """



class Redis(object):
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        '''
        Initialize script object - The Script object ensures that the LUA script is loaded into Redis's script cache. 
        In the event of a NOSCRIPT error, it will load the script and retry executing it.
        '''
        self.getDevice = self.redis.register_script(LUA_GET)


        '''if 'device1' on redis server, load it with default info'''
        # self.getDevice(keys=['device1'],args=[json.dumps(DEVICES['device1'])])


    
    def set(self,key,data):
       self.redis.set(key,json.dumps(data))
       return self.get(key)

    def get(self,key):

        data = self.getDevice(keys=[key],args=[json.dumps(DEVICES[key])])

        return json.loads(data)


    # def delete(self,key):

'''Initialize REDIS object'''
REDIS = Redis()


''''''''''''''''''''''''''''''''''''
'''Single Device Response Methods'''
''''''''''''''''''''''''''''''''''''
@api.route('/Devices/<string:device_id>', methods=['GET','POST','PUT'])
@api.doc(responses={404: 'Device not found', 200: 'Device found'}, params={'device_id': 'The Device ID'},)
@api.doc(description='device_id should be {0}'.format(', '.join(DEVICES.keys())))
class Device(Resource):
    '''Show a single device's properties and lets you delete them or change them'''
    @api.response(200, 'Success', device)
    def get(self, device_id):
        '''Fetch a given resource'''
        abort_if_device_not_found(device_id)
        redisGet = REDIS.get(device_id)
        print('redisGet: ', redisGet)
        return jsonify(redisGet)
        # return jsonify(DEVICES[device_id],200)
        
    @api.doc(responses={204: 'Device deleted'})
    def delete(self, device_id):
        '''Delete a given resource'''
        abort_if_device_not_found(device_id)
        del DEVICES[device_id]
        return '', 204

    @api.expect(device, validate=True)
    # @api.doc(parser=parser)
    @api.response(200, 'Success', device)
    def put(self, device_id):
        '''Update a given resource's onState or brightness properties'''
        if 'onState' in request.json:
            # print("onState found")
            DEVICES[device_id]['onState'] =request.json.get('onState',DEVICES[device_id]['onState'])
            print('new onState value stored: ', DEVICES[device_id]['onState'])
        if 'brightness' in request.json:
            newbrightness=request.json.get('brightness',DEVICES[device_id]['brightness'])
            # print('newbrightness =', newbrightness)
            DEVICES[device_id]['brightness']=newbrightness
            print('new brightness value stored: ', DEVICES[device_id]['brightness'])
        if 'name' in request.json:
            newbrightness=request.json.get('name',DEVICES[device_id]['name'])
            # print('newbrightness =', newbrightness)
            DEVICES[device_id]['name']=newbrightness
            print('new name stored: ', DEVICES[device_id]['name'])

        # print(DEVICES[device_id])
        redisSet = REDIS.set(device_id, DEVICES[device_id])
        print('redisSet = ', redisSet)
        return jsonify(redisSet)
        # return jsonify(DEVICES[device_id])


''''''''''''''''''''''''''''''''''''''
'''List of Devices Response Methods'''
''''''''''''''''''''''''''''''''''''''
@api.route('/Devices/')
class DeviceList(Resource):
    '''Shows a list of all devices, and lets you POST to add new tasks'''
    @api.response(200, 'Success', list_of_devices)
    def get(self):
        '''Return a list of all devices and their properties'''
        print("returning Device List: ", DEVICES)
        return jsonify(DEVICES)    
        # return ([{'id': id, 'device': ListedDevices} for id, ListedDevices in DEVICES.items()],
                 # 200)

    @api.expect(device, validate=True)
    def post(self):
        '''Create a new device with next id'''       
        device_id = 'device%d' % (len(DEVICES) + 1)
        DEVICES[device_id] = device

        '''populate device properties with request contents if there'''
        if 'onState' in request.json:
            print("onState found")
            DEVICES[device_id]['onState'] =request.json.get('onState',DEVICES[device_id]['onState'])
            print(DEVICES[device_id]['onState'])
        if 'brightness' in request.json:
            DEVICES[device_id]['brightness']=request.json.get('brightness',DEVICES[device_id]['brightness'])
            print('brightness found')
        if 'name' in request.json:
            DEVICES[device_id]['name']=request.json.get('name',DEVICES[device_id]['name'])
            print('name found')
            
        # print(DEVICES[device_id])
        redisSet = REDIS.set(device_id, DEVICES[device_id])
        print('redisSet = ', redisSet)
        return jsonify(redisSet)
        # return jsonify(DEVICES[device_id], 201)

@app.errorhandler(404)
def not_found(error):
    return (jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    