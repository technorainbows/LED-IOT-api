#!/usr/bin/env python

from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, cors
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='0.2', title='LED API',
    description='A simple LED IOT API', doc='/docs'
)

ns = api.namespace('Devices', description='DEVICES operations')


DEVICES = {
    'device1': 
        {
            'OnState': False, 
            'Brightness': 200,
            'Name':'Ashley-Triangle'
        },
    'device2': 
        {
            'OnState': True, 
            'Brightness': 100,
            'Name':'Other"'
        }
}


device = api.model('Device', {
    'OnState': fields.Boolean(description='The on/off state', attribute='OnState', required=True, default=True),
    'Brightness': fields.Integer(description='The LED Brightness', attribute='Brightness', min=0, max=255, required=True, default=255),
    'Name': fields.String(description="Name of the device", attribute='Name', default='None')
})


listed_lights = api.model('ListedDevices', {
    'id': fields.String(required=True, description='The device ID'),
    'device': fields.Nested(device, description='The device')
})


def abort_if_device_not_found(device_id):
    if device_id not in DEVICES:
        api.abort(404, "Device {} doesn't exist".format(device_id))



parser = api.parser()
parser.add_argument('device',  required=True, help='The device details', location='form')


@ns.route('/<string:device_id>')
@api.doc(responses={404: 'Device not found'}, params={'device_id': 'The Device ID'})
@api.doc(description='device_id should be in {0}'.format(', '.join(DEVICES.keys())))
class Device(Resource):
    '''Show a single device's properties and lets you delete them or change them'''
    @api.doc(description='device_id should be in {0}'.format(', '.join(DEVICES.keys())))
    @api.marshal_with(device)
    @cors.crossdomain(origin='*', headers='content-type')
    def get(self, device_id):
        '''Fetch a given resource'''
        abort_if_device_not_found(device_id)
        return jsonify(DEVICES[device_id])

    @api.doc(responses={204: 'Device deleted'})
    @cors.crossdomain(origin='*', headers=['content-type'], methods=['delete'])
    def delete(self, device_id):
        '''Delete a given resource'''
        abort_if_device_not_found(device_id)
        del DEVICES[device_id]
        return '', 204

    @api.expect(device, validate=True)
    @api.doc(parser=parser)
    @api.marshal_with(device)
    @cors.crossdomain(origin='*', headers=['content-type'], methods=['put'])
    def put(self, device_id):
        '''Update a given resource's OnState or Brightness properties'''
        if 'OnState' in request.json:
            print("OnState found")
            DEVICES[device_id]['OnState'] =request.json.get('OnState',DEVICES[device_id]['OnState'])
            print(DEVICES[device_id]['OnState'])
        if 'Brightness' in request.json:
            DEVICES[device_id]['Brightness']=request.json.get('Brightness',DEVICES[device_id]['Brightness'])
            print('brightness found')
        print(DEVICES[device_id])
        return jsonify(DEVICES[device_id])
        # DEVICES[device_id] = device
        # return device

@ns.route('/')
class DeviceList(Resource):
    '''Shows a list of all devices, and lets you POST to add new tasks'''
    @api.marshal_list_with(listed_lights)
    # @cors.crossdomain(origin='*', headers=['content-type'], methods='get')
    def get(self):
        '''List all devices'''
        # return DEVICES
        print("returning Device List: ", DEVICES)
        # for id, ListedDevices in DEVICES.items():
        #     return jsonify([{'id': id, 'device':ListedDevices}])
        # return jsonify(DEVICES)    
        return ([{'id': id, 'device': ListedDevices} for id, ListedDevices in DEVICES.items()],200)

    # @api.doc(params={'device'})
    @api.marshal_with(device, code=201)
    @api.expect(device, validate=True)
    @cors.crossdomain(origin='*', headers=['content-type'], methods=['post'])
    def post(self):
        '''Create a new device with next id'''       
        device_id = 'device%d' % (len(DEVICES) + 1)
        DEVICES[device_id] = device

        '''populate device properties with request contents if there'''
        if 'OnState' in request.json:
            print("OnState found")
            DEVICES[device_id]['OnState'] =request.json.get('OnState',DEVICES[device_id]['OnState'])
            print(DEVICES[device_id]['OnState'])
        if 'Brightness' in request.json:
            DEVICES[device_id]['Brightness']=request.json.get('Brightness',DEVICES[device_id]['Brightness'])
            print('brightness found')
        if 'Name' in request.json:
            DEVICES[device_id]['Name']=request.json.get('Name',DEVICES[device_id]['Name'])
            print('name found')
            
        print(DEVICES[device_id])
        return jsonify(DEVICES[device_id], 201)

@app.errorhandler(404)
def not_found(error):
    return (jsonify({'error': 'Not found'}), 404)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    