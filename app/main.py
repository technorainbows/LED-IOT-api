#!/usr/bin/env python3 -u

"""API for LED IOT webapp."""
import os
import sys
import logging
import logging.config
import json
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
# from werkzeug.contrib.fixers import ProxyFix
import redis
from redis.exceptions import WatchError
from modules.auth_decorator import validate_access


# Set up simple logging.
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Get LOG_LEVEL from environment if set, otherwise set to default
if 'LOG_LEVEL' not in os.environ:
    logging.warning("LOG_LEVEL not set, using default")
    LOG_LEVEL = logging.DEBUG
else:
    # Check if env variable correponds to logging level word or number.
    try:
        # getattr(logging, os.environ['LOG_LEVEL'].upper())
        LOG_LEVEL = getattr(logging, os.environ['LOG_LEVEL'].upper())
        logging.info("1. LOG_LEVEL set to: %s", LOG_LEVEL)

    except AttributeError:
        TEMP_LEVEL = logging.getLevelName(int(os.environ['LOG_LEVEL']))
        logging.info("temp_level got from env: %s", TEMP_LEVEL)

        if not TEMP_LEVEL.startswith('Level'):
            LOG_LEVEL = TEMP_LEVEL
            logging.info("2. INT LOG_LEVEL set to: %s", LOG_LEVEL)
        else:
            LOG_LEVEL = logging.WARNING
            logging.warning(
                "Incorrect LOG_LEVEL provided (%s). Setting to WARNING.", TEMP_LEVEL)
    except Exception:
        logging.error("Error with LOG_LEVEL provided. Using default.")
        LOG_LEVEL = logging.WARNING

logging.getLogger().setLevel(LOG_LEVEL)

# Set heartbeat TTL via environment variable if avail, else set to default.
if 'HB_EXP' in os.environ:
    HB_EXP = int(os.environ['HB_EXP'])
    logging.info("HB_EXP has been set via env")
else:
    logging.warning("No HB_EXP set; using default (10). ")
    HB_EXP = 10

# load and parse client secrets file
with open('./client_secrets.json', 'r') as myfile:
    data = myfile.read()
data = json.loads(data)
logging.debug(data)
client_secrets = data['web']



class Server(object):
    """Flask app and api methods."""

    def __init__(self):
        """Initialize Flask app and api."""
        self.app = Flask(__name__)
        self.app.config.SWAGGER_UI_OAUTH_CLIENT_ID = client_secrets['client_id']
        self.app.config.SWAGGER_UI_OAUTH_REALM = '-'
        self.app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
        # self.app.config.SWAGGER_UI_OAUTH_APP_NAME = 'Demo'
        # api = Api(app, security='Bearer Auth', authorizations=authorizations)

        authorizations = {
            'OAuth2': {
                'type': 'oauth2',
                'flow': 'implicit',
                'authorizationUrl': client_secrets['auth_uri'],
                'clientId': self.app.config.SWAGGER_UI_OAUTH_CLIENT_ID,
                'clientSecret': client_secrets['client_secret'],
                'scopes': {
                    'read': 'Grant read-only access',
                    'write': 'Grant read-write access',
                }
            },
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            },
        }

        self.api = Api(self.app,
                       version='0.4',
                       title='LED API',
                       description='A simple LED IOT API',
                       doc='/docs',
                       security=['Bearer Auth', {'OAuth2': 'read'}],
                       authorizations=authorizations
                      )

        CORS(self.app)

    def run(self):
        """Run flask app."""
        self.app.run(debug=True,
                     port=80)


server = Server()
APP = server.app
API = server.api
CORS(APP)
# APP = Flask(__name__)
# APP.wsgi_app = ProxyFix(APP.wsgi_app)
# API = Api(APP, version='0.4', title='LED API',
#   description='A simple LED IOT API', doc='/docs'
#   )


# ns = API.namespace('Devices', description='DEVICES operations')

# Default device settings.
DEFAULT = {
    'onState': 'true',
    'brightness': '255',
    'name': 'Default'
}


# Single Device Data Model
DEVICE = API.model('Device', {
    'onState': fields.String(description='The on/off state',
                             attribute='onState',
                             required=False,
                             default=True),
    'brightness': fields.String(description='The LED brightness',
                                attribute='brightness',
                                min=0,
                                max=255,
                                required=False,
                                default=255),
    'name': fields.String(description="name of the device",
                          attribute='name',
                          required=False,
                          default='N/A')
})

# Device List Data Model
LIST_OF_DEVICES = API.model('ListedDevices', {
    'id': fields.String(required=True, description='The device ID'),
    'device': fields.Nested(DEVICE, description='The device'),
})

HEARTBEAT = API.model('Heartbeat', {
    'heartbeat': fields.String(required=False, description='Device heartbeat')
})


class Redis(object):
    """Class for manipulating redis client."""

    def __init__(self):
        """Initialize Redis Object."""
        if 'REDIS_HOST' in os.environ:
            REDIS_HOST = os.environ['REDIS_HOST']
            self.redis = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        else:
            try:
                raise Exception
            except Exception:
                logging.error('REDIS_HOST not set.')
                sys.exit("!!!Exiting. Please set REDIS_HOST in env & restart.")

    def get(self, key):
        """Get device from redit if it exists, otherwise load with DEFAULT."""
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    if pipe.exists(key) == 0:
                        logging.warning("get: no device")
                        pipe.multi()
                        pipe.hmset(key, DEFAULT)
                        # time.sleep(5)
                        pipe.execute()
                        device = DEFAULT
                        break
                    else:
                        device = pipe.hgetall(key)
                        # logging.info("get: device found %s ", device)
                        # Initialising empty dictionary
                        new_dict = {}

                        # Convert dictionary items from bytes to strings
                        for dkey, value in device.items():
                            new_dict[dkey.decode(
                                "utf-8")] = value.decode("utf-8")
                        device = new_dict
                        logging.debug("get: device found: %s", str(device))
                        break
                except WatchError:
                    logging.warning("get: watcherror, trying again")
                    continue
                except redis.ConnectionError:
                    logging.exception("Connection error")
                except Exception:
                    logging.exception("Unexpected error")

        return device

    def set(self, key, field, value):
        """Set value if device exists, else first initialize device to DEFAULT."""
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    if pipe.exists(key) == 0:
                        logging.warning("set: no device")
                        pipe.hmset(key, DEFAULT)
                        print("field: ", field, " value: ", value)
                        pipe.hmset(key, {field: value})
                        # time.sleep(5)
                        device = pipe.hgetall(key)
                        pipe.execute()
                        logging.info("set: device now: %s", str(device))
                        break

                    else:
                        pipe.hmset(key, {field: value})
                        device = pipe.hgetall(key)
                        logging.info("set: device found: %s", str(device))
                        break

                except WatchError:
                    logging.warning("set: watcherror, trying again")
                    continue
                except ConnectionError:
                    logging.exception("Connection error")
                except Exception:
                    logging.exception("Unexpected error occured")

            # Initialising empty dictionary
            new_dict = {}

            # Convert dictionary items from bytes to strings
            for dkey, value in device.items():
                new_dict[dkey.decode("utf-8")] = value.decode("utf-8")
            device = new_dict
            logging.info("Set: new device = %s", str(device))

            return device

    def delete(self, key):
        """Delete a key from Redis client."""
        try:
            response = self.redis.delete(key)
            logging.info("response: %s", str(response))

        except ConnectionError:
            logging.exception("Connection error")
        except Exception:
            logging.exception("Unexpected error occured")
        return response

    def keys(self, param):
        """Return list of all keys matching parameter."""
        keys = []
        try:
            for key in self.redis.scan_iter(match=param+"*"):
                print("key: ", key)
                keys.append(key.decode())
            # logging.debug("keys returned: ", keys)

        except ConnectionError:
            logging.exception("Connection error")
        except Exception:
            logging.exception("Unexpected error occured")
        return keys

    def set_hb(self, heartbeat):
        """Set heartbeat key in redis that expires in provided time."""
        try:
            response = self.redis.setex(
                heartbeat, HB_EXP, "none")  # name, time, value
            logging.info("heartbeat set")

        except ConnectionError:
            logging.exception("Connection error")
        except Exception:
            logging.exception("Unexpected error")
        return response


# Initialize REDIS object
REDIS = Redis()


#########################
#   Heartbeat Methods   #
#########################
@API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
@API.route('/Devices/HB/<string:device_id>', methods=['GET', 'POST'])
class Heartbeat(Resource):
    """Update and check on a given device's heartbeat/online status."""

    @validate_access
    @API.response(200, 'Success')
    def get(self, device_id):
        """Check if a given heartbeat exists."""
        logging.debug("checking device HB")
        heartbeat = "hb_" + device_id
        response = REDIS.keys(heartbeat)
        logging.debug("HB get response = %s", str(response))
        if response == []:
            logging.error('Error, device not found')
            return ('Error, device not found', 404)
        else:
            return jsonify(response)

    @API.response(200, 'Success')
    # @API.param('heartbeat')
    @API.expect(HEARTBEAT, validate=False)
    @validate_access
    def post(self, device_id):
        """Set a heartbeat."""
        # hbTime = 15
        heartbeat = "hb_" + device_id
        response = REDIS.set_hb(heartbeat)
        logging.warning("HB post response = %s", response)
        payload = API.payload
        logging.info("payload = %s", payload)
        if response:
            logging.warning("heartbeat set: %s", response)
            return jsonify(response)
        else:
            logging.error("Error, failed to set heartbeat")
            return "Error, failed to set heartbeat.", 404

# @validate_access
@API.route('/Devices/HB/', methods=['GET'])
class Heartbeats(Resource):
    """Monitor which devices are online or not via heartbeat."""

    @API.response(202, 'Success')
    @API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
    @validate_access
    def get(self):
        """Return a list of all heartbeats."""
        logging.debug("Getting all HB keys")
        keys = REDIS.keys("hb")
        logging.debug("*******HB keys retrieved: %s", keys)
        return jsonify(keys)


##################################
# Single Device Response Methods #
##################################
# TODO: add list of device_ids from redis to check if decive there
@API.route('/Devices/<string:device_id>',
           methods=['GET', 'POST', 'PUT', 'DELETE'])
@API.doc(responses={404: 'Device not found', 200: 'Device found'},
         params={'device_id': 'The Device ID'})
@API.doc(description='device_id should be {0}'.format(
    ', '.join(REDIS.keys("device_id"))))
@API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
# @validate_access
class Device(Resource):
    """Show a device's properties and let user delete or change properties."""

    @validate_access
    @API.response(200, 'Success', DEVICE)
    def get(self, device_id):
        """Fetch a given resource."""
        # abort_if_device_not_found(device_id)
        redis_get = REDIS.get(device_id)
        # print("device_id: ", device_id)
        # print('redis_get: ', redis_get)
        return jsonify(device_id, redis_get)
        # return jsonify(DEVICES[device_id],200)

    @API.doc(responses={200: 'Device deleted'})
    @validate_access
    def delete(self, device_id):
        """Delete a given resource."""
        # abort_if_device_not_found(device_id)
        response = REDIS.delete(device_id)
        logging.info("REDIS delete response: %s", str(response))
        if response:
            logging.info("Device deleted: %s", device_id)
            return jsonify('Device deleted', 200)
        else:
            logging.error('Error, device not found: %s', device_id)
            return jsonify('Error: device not found', 404)

    @API.expect(DEVICE, validate=True)
    # @API.doc(parser=parser)
    @API.response(200, 'Success', DEVICE)
    @validate_access
    def put(self, device_id):
        """Update a given resource's field with new property value received."""
        logging.info("PUT request received")
        for field in DEVICE:
            if field in request.json:
                # print("field found: ", field, "value = ", request.json.get(field))
                # let value = request.json.get(field)
                REDIS.set(device_id, field, request.json.get(field))

        # print('returned redisSet = ', redisSet)
        return jsonify(device_id, REDIS.get(device_id), 200)


####################################
# List of Devices Response Methods #
####################################
@API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
@API.route('/Devices/')
# @validate_access
class DeviceList(Resource):
    """Shows a list of all devices, and lets you POST to add new tasks."""
    @API.doc(security=[{'oath2': ['read', 'write']}])
    @validate_access
    @API.response(200, 'Success', LIST_OF_DEVICES)
    def get(self):
        """Return a list of all devices and their properties."""
        devices = REDIS.keys("device_")
        logging.debug("returning Device List: %s", str(devices))
        return jsonify(devices, 200)

    @validate_access
    @API.expect(DEVICE, validate=True)
    def post(self):
        """Create a new device with next id."""
        # TODO: check if this does anything
        device_id = 'device%d' % (len(DEVICE) + 1)
        # DEVICES[device_id] = device
        logging.info("json request received: %s", str(request.json))

        # Update a given resource's field with new property value received.
        for field in DEVICE:
            # print("field: ", field)
            if field in request.json:
                # print("field found: ", field, "value = ", request.json.get(field))
                REDIS.set(device_id, field, request.json.get(field))

        return jsonify(device_id, REDIS.get(device_id), 201)


@APP.errorhandler(404)
def not_found(error_rec):
    """Return not found error message."""
    logging.error('Error: %s', error_rec)
    return (jsonify({'error_handler': error_rec}), 404)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True,
            ssl_context=('certificates/localhost.crt', 'certificates/device.key'))
