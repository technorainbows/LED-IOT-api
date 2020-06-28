#!/usr/bin/env python3 -u

"""API for LED IOT webapp."""
import os
import sys
import logging
import logging.config
import json
from flask_cors import CORS
from flask import Flask, jsonify, request, make_response
from flask_restplus import Api, Resource, fields, abort
import redis
from redis.exceptions import WatchError, ConnectionError, TimeoutError
from modules.auth_decorator import validate_access
import traceback
from werkzeug.exceptions import HTTPException, NotFound

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
    DATA = myfile.read()
DATA = json.loads(DATA)
CLIENT_SECRETS = DATA['web']


class Server(object):
    """Flask app and api methods."""

    def __init__(self):
        """Initialize Flask app and api."""
        logging.debug("initializing Sever app")
        self.app = Flask(__name__)
        self.app.config.SWAGGER_UI_OAUTH_CLIENT_ID = CLIENT_SECRETS['client_id']
        self.app.config.SWAGGER_UI_OAUTH_REALM = '-'
        self.app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

        authorizations = {
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            },
        }

        self.api = Api(self.app,
                       title='LED API',
                       description='A simple LED IOT API',
                       host='api.ashleynewton.net',
                       doc='/docs',
                       security=['Bearer Auth',
                                 #    {'OAuth2': ['read', 'write']}
                                 ],
                       authorizations=authorizations
                       )

        CORS(self.app)

    def run(self):
        """Run flask app."""
        logging.debug("running Server app")
        self.app.run(debug=True,
                     port=80)


server = Server()
APP = server.app
API = server.api
# CORS(APP)

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

REDIS_LOCAL = True  # toggle this to use local redis client for development purposes


class Redis(object):
    """Class for manipulating redis client."""

    def __init__(self):
        """Initialize Redis Object."""
        if REDIS_LOCAL:
            REDIS_HOST = '127.0.0.1'
            self.redis = redis.Redis(
                host=REDIS_HOST, port=6379, db=0)
            logging.warning("Using local development REDIS")
        else:
            if 'REDIS_HOST' in os.environ:
                REDIS_HOST = os.environ['REDIS_HOST']
                if 'REDIS_PASSWORD' in os.environ:
                    REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
                    logging.info("Redis password found %s", REDIS_PASSWORD)
                    self.redis = redis.Redis(
                        host=REDIS_HOST, port=6379, db=0, password=REDIS_PASSWORD)
                else:
                    logging.info(
                        "No redis password found, initializing without auth")
                    self.redis = redis.Redis(host=REDIS_HOST, port=6379, db=0)
            else:
                logging.error('REDIS_HOST not set.')
                sys.exit("!!!Exiting. Please set REDISi s_HOST in env & restart.")

    def health(self):
        """Return a ping response from redis client."""
        return self.redis.ping()

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
                        pipe.execute()
                        device = DEFAULT
                        break
                    else:
                        device = pipe.hgetall(key)
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
                        pipe.hmset(key, {field: value})
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
        response = self.redis.delete(key)
        logging.info("REDIS_DELETE: response: %s", str(response))

        if response == 0:
            logging.debug("REDIS_DELETE: returning notfound")
            raise NotFound("Device wasn't here. Ooops.")
        logging.debug("REDIS_DELETE: returning 1")
        return 1  # return 1 (true) if delete was successful

    def keys(self, param):
        """Return list of all keys matching parameter."""
        keys = []
        results = self.redis.scan_iter(match=param + "*")
        logging.debug("KEYS: results = %s", str(results))

        for key in results:
            logging.debug("key: %s", key)
            keys.append(key.decode())
        logging.debug("KEYS: returning keys: %s", keys)
        return keys

    def set_hb(self, heartbeat):
        """Set heartbeat key in redis that expires in provided time."""
        response = self.redis.setex(
            heartbeat, HB_EXP, "none")  # name, time, value
        logging.info("SET_HB: heartbeat set")
        return response


# Initialize REDIS object
REDIS = Redis()


#########################
#   Heartbeat Methods   #
#########################
# @API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
@API.doc(responses={401: 'Unauthorized', 404: 'Incorrect request', 502: 'Server error'})
@API.route('/devices/hb/<string:device_id>', methods=['GET', 'POST'])
class Heartbeat(Resource):
    """Update and check on a given device's heartbeat/online status."""

    @validate_access
    @API.response(200, 'Found device', LIST_OF_DEVICES['id'])
    def get(self, device_id):
        """Check if a given heartbeat exists."""
        logging.debug("checking device HB")
        heartbeat = "hb_" + device_id
        try:
            response = REDIS.keys(heartbeat)
            logging.debug("HB get response = %s", str(response))
            return jsonify(response)
        except Exception as error:
            logging.error('Error getting keys')
            raise error

    @API.response(201, 'Successly set heartbeat for device')
    @API.expect(HEARTBEAT, validate=False)
    @validate_access
    def post(self, device_id):
        """Set a heartbeat."""
        heartbeat = "hb_" + device_id
        try:
            response = REDIS.set_hb(heartbeat)
            logging.info("HB post response = %s", response)
            payload = API.payload
            logging.info("payload = %s", payload)
            if response:
                logging.info("heartbeat set: %s", response)
                return make_response(jsonify({'message': 'Heartbeat set'}), 201)

        except Exception as error:
            logging.error("error setting heartbeat: %s", type(error))
            raise error


@API.doc(responses={401: 'Unauthorized', 404: 'Incorrect request', 502: 'Server error'})
@API.route('/devices/hb/', methods=['GET'])
class Heartbeats(Resource):
    """Monitor which devices are online or not via heartbeat."""

    @API.response(200, 'Successly retreived device keys')
    @validate_access
    def get(self):
        """Return a list of all heartbeats."""
        logging.debug("Getting all HB keys")
        try:
            keys = REDIS.keys("hb")
            logging.debug("*******HB keys retrieved: %s", keys)
            return jsonify(keys)
        except Exception as error:
            logging.error("HB_GET: ERROR getting keys")
            raise error


##################################
# Single Device Response Methods #
##################################
# TODO: add list of device_ids from redis to check if decive there
@API.route('/devices/<string:device_id>',
           methods=['GET', 'POST', 'PUT', 'DELETE'])
@API.doc(responses={401: 'Unauthorized', 404: 'Incorrect request', 502: 'Server error'},
         params={'device_id': 'The Device ID'})
# @API.doc(description='device_id should be {}'.format(' '.join(REDIS.keys("device_"))))
# @API.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer ${api key}'}})
class Device(Resource):
    """Show a device's properties and let user delete `or change properties."""

    @validate_access
    @API.response(200, 'Success: device retrieved.', DEVICE)
    def get(self, device_id):
        """Fetch a given resource."""
        try:
            redis_get = REDIS.get(device_id)
            return jsonify(device_id, redis_get)
        except Exception as error:
            logging.error("Error encountered: %s", error)
            raise error

    @API.doc(responses={200: 'Device deleted', 404: 'Device not found'})
    @validate_access
    def delete(self, device_id):
        """Delete a given resource."""
        logging.info("About to delete this thing... %s", device_id)
        try:
            response = REDIS.delete(device_id)
            logging.info("REDIS delete response: %s", str(response))
            logging.info("Success: device deleted: %s", device_id)
            return jsonify({'message': 'Successly deleted device'})

        except Exception as error:
            logging.error("DELETE: error encountered")
            raise error

    @API.expect(DEVICE, validate=True)
    @API.response(201, 'Success: device updated.', DEVICE)
    @validate_access
    def put(self, device_id):
        """Update a given resource's field with new property value received."""
        logging.info("PUT request received")
        for field in DEVICE:
            if field in request.json:
                try:
                    REDIS.set(device_id, field, request.json.get(field))
                except Exception as error:
                    logging.error("REDIS.set error: %s",
                                  traceback.format_exception_only(type(error), error))
                    raise error
        try:
            return make_response(jsonify(device_id, REDIS.get(device_id)), 201)
        except Exception as error:
            logging.error("ERROR ENCOUNTERED: %s",
                          traceback.format_exception_only(type(error), error))
            raise error

####################################
# List of devices Response Methods #
####################################
@API.doc(responses={401: 'Unauthorized', 404: 'Incorrect request', 502: 'Server error'})
@API.route('/devices/')
class DeviceList(Resource):
    """Shows a list of all devices, and lets you POST to add new tasks."""

    # @API.doc(security=[{'oath2': ['read', 'write']}])
    @validate_access
    @API.response(200, 'Success', LIST_OF_DEVICES)
    def get(self):
        """Return a list of all devices and their properties."""
        try:
            devices = REDIS.keys("device_")
            logging.debug("returning Device List: %s", str(devices))
            return make_response(jsonify(devices), 201)
        except Exception as error:
            logging.error("DEVICELIST/GET: %s",
                          traceback.format_exception_only(type(error), error))
            raise error

    @validate_access
    @API.expect(DEVICE, validate=True)
    @API.response(201, 'Device created')
    def post(self):
        """Create a new device with next id."""
        # TODO: check if this does anything
        device_id = 'device%d' % (len(DEVICE) + 1)
        logging.info("json request received: %s", str(request.json))

        # Update a given resource's field with new property value received.
        for field in DEVICE:
            if field in request.json:
                try:
                    REDIS.set(device_id, field, request.json.get(field))
                except Exception as error:
                    logging.error("Redis SET error")
                    raise error
        try:
            return make_response(jsonify(device_id, REDIS.get(device_id)), 201)
        except Exception as error:
            logging.error("error getting device after creating")
            raise error


@API.doc(responses={200: 'Server healthy', 502: 'Server error'})
@API.route('/health', methods=['GET'])
class Health(Resource):
    """Health check endpoint."""

    def get(self):
        """Return health status of redis client."""
        try:
            redis_healthy = REDIS.health()

            if redis_healthy is True:
                logging.info('Health: healthy')
                return 200

            logging.error('Health: %s', redis_healthy)
            return {'Health': redis_healthy}, 502
        except Exception as error:
            logging.error("GET Error encountered")
            raise error


@APP.errorhandler(ConnectionError)
@API.errorhandler(ConnectionError)
def connection_error(error_rec):
    """Return server error message."""
    logging.error('ERROR-HANDLER: ConnectionError')
    return (jsonify({'message': 'ConnectionError'}), 502)


@APP.errorhandler(401)
def auth_error(error_rec):
    """Return server error message."""
    logging.error('ERROR-HANDLER: Authentication Error: %s', error_rec)
    return (jsonify({'Authentication error': str(error_rec)}), 403)


if __name__ == '__main__':
    logging.debug("attempting APP.run")
    APP.run(host='0.0.0.0', port=5000, debug=True)
