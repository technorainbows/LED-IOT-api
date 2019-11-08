#!/usr/bin/env python3 -u

"""API for LED IOT webapp."""
import os
import sys
import logging
import logging.config
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
# from werkzeug.contrib.fixers import ProxyFix
import redis
from redis.exceptions import WatchError
# import json

# import yaml
# import traceback

# Set up simple logging.
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)

# LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
#                    sorted(getattr(logging, '_levelToName', None)
#                           or logging._levelNames)
#                    if getattr(v, "real", 0)]

# Get LOG_LEVEL from environment if set, otherwise set to default
if 'LOG_LEVEL' not in os.environ:
    logging.warning("LOG_LEVEL not set, using default")
    LOG_LEVEL = logging.WARNING
else:
    # Check if env variable correponds to logging level word or number.
    try:
        # getattr(logging, os.environ['LOG_LEVEL'].upper())
        LOG_LEVEL = getattr(logging, os.environ['LOG_LEVEL'].upper())
        logging.info("1. LOG_LEVEL set to: %s", LOG_LEVEL)

    except AttributeError:
        TEMP_LEVEL = logging.getLevelName(int(os.environ['LOG_LEVEL']))
        logging.info("temp_level got from env: %s", TEMP_LEVEL)
        # print(type(TEMP_LEVEL))
        # TEMP_LEVEL = logging.getLevelName(TEMP_LEVEL)
        if not TEMP_LEVEL.startswith('Level'):
            LOG_LEVEL = TEMP_LEVEL
        # try:
        #     LOG_LEVEL = get_levels(TEMP_LEVEL)
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


class Server(object):
    """Initialize and run Flask app and api as method for import."""

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app,
                       version='0.4',
                       title='LED API',
                       description='A simple LED IOT API',
                       doc='/docs'
                       )
        CORS(self.app)

    def run(self):
        """Run flask app."""

        self.app.run(debug=environment_config["debug"],
                     port=environment_config["port"])


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


# def abort_if_device_not_found(device_id):
#     if device_id not in DEVICES:
#         API.abort(404, "Device {} doesn't exist".format(device_id))


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
                        logging.info("get: no device")
                        pipe.multi()
                        pipe.hmset(key, DEFAULT)
                        # time.sleep(5)
                        pipe.execute()
                        device = DEFAULT
                        break
                    else:
                        device = pipe.hgetall(key)
                        logging.info("get: device found %s ", device)
                        # Initialising empty dictionary
                        new_dict = {}

                        # Convert dictionary items from bytes to strings
                        for dkey, value in device.items():
                            new_dict[dkey.decode(
                                "utf-8")] = value.decode("utf-8")
                        device = new_dict
                        logging.info("get: device found: %s", str(device))
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
                        logging.info("set: no device")
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
                # print("key: ", key)
                keys.append(key.decode())
            # print("keys returned: ", keys)

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
@API.route('/Devices/HB/<string:device_id>', methods=['GET', 'POST'])
class Heartbeat(Resource):
    """Update and check on a given device's heartbeat/online status."""

    @API.response(200, 'Success')
    def get(self, device_id):
        """Check if a given heartbeat exists."""
        logging.info("checking device HB")
        heartbeat = "hb_" + device_id
        response = REDIS.keys(heartbeat)
        logging.info("HB get response = %s", str(response))
        if response == []:
            logging.error('Error, device not found')
            return ('Error, device not found', 404)
        else:
            return jsonify(response)

    @API.response(200, 'Success')
    # @API.param('heartbeat')
    @API.expect(HEARTBEAT, validate=False)
    def post(self, device_id):
        """Set a heartbeat."""
        # hbTime = 15
        heartbeat = "hb_" + device_id
        response = REDIS.set_hb(heartbeat)
        logging.info("HB post response = %s", response)
        payload = API.payload
        logging.info("payload = %s", payload)
        if response:
            return jsonify(response)
        else:
            logging.error("Error, failed to set heartbeat")
            return "Error, failed to set heartbeat.", 404


@API.route('/Devices/HB/', methods=['GET'])
class Heartbeats(Resource):
    """Monitor which devices are online or not via heartbeat."""

    @API.response(202, 'Success')
    def get(self):
        """Return a list of all heartbeats."""
        keys = REDIS.keys("hb")
        logging.info("HB getting all keys: %s", keys)
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
class Device(Resource):
    """Show a device's properties and let user delete or change properties."""

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
    def put(self, device_id):
        """Update a given resource's field with new property value received."""
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
@API.route('/Devices/')
class DeviceList(Resource):
    """Shows a list of all devices, and lets you POST to add new tasks."""

    @API.response(200, 'Success', LIST_OF_DEVICES)
    def get(self):
        """Return a list of all devices and their properties."""
        devices = REDIS.keys("device_")
        logging.info("returning Device List: %s", str(devices))
        return jsonify(devices, 200)

    @API.expect(DEVICE, validate=True)
    def post(self):
        """Create a new device with next id."""
        # TODO: check if this does anything
        device_id = 'device%d' % (len(DEVICE) + 1)
        # DEVICES[device_id] = device
        # print("json request received: ", request.json)

        # Update a given resource's field with new property value received.
        for field in DEVICE:
            # print("field: ", field)
            if field in request.json:
                # print("field found: ", field, "value = ",request.json.get(field))
                REDIS.set(device_id, field, request.json.get(field))

        return jsonify(device_id, REDIS.get(device_id), 201)


@APP.errorhandler(404)
def not_found(error_rec):
    """Return not found error message."""
    logging.error('Error, device not found: %s', error_rec)
    return (jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=80, debug=True)
