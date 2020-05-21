"""Authentication wrapper."""

import os
import json
# import time
from functools import wraps
import logging
import logging.config
from flask import Flask, request, make_response, jsonify
import jwt
# from jwt.algorithms import RSAAlgorithm, HMACAlgorithm, get_default_algorithms


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

with open('./client_secrets.json', 'r') as myfile:
    data = myfile.read()

# parse client secrets file
# data = os.getenv('CLIENT_SECRETS')
data = json.loads(data)
# print(data)
client_secrets = data['web']
# print(json.dumps(data))


def validate_access(func):
    """Authenticate user."""
    @wraps(func)
    def wrapper_validate_access(*args, **kwargs):
        """Validate access."""
        # decode and verify header
        # for i in args:
        #     print("args:", i.value)
        logging.debug("in wrapper")
        # print("request: ", request.headers)
        access_token = None

        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            access_token = request.headers['Authorization'].split(None, 1)[
                1].strip()
            # print("token found: ", access_token)
            try:
                header = jwt.get_unverified_header(access_token)
                logging.info("unverified header: %s", header)

                # if header validated, then decode/check claims
                # assert(header['kid'] == kid)
                # try:
                claims = jwt.decode(
                    access_token, client_secrets['client_secret'], verify=False)
                # print("claims = ", claims)
                # try:
                if (claims['cid'] == client_secrets['cid']) and (claims['aud'] == client_secrets['aud']):
                    logging.info("token validated!!")

                    if claims['sub'] in client_secrets['allowed_users']:
                        logging.info("user permitted! - %s", claims['sub'])
                        return func(*args, **kwargs)
                    else:
                        # print("user not allowed")
                        return make_response({'error': 'user not allowed'}, 403)
                logging.error("claims not validated")

            except ValueError:
                logging.error("***********unable to decode header")
                return {'ValueError': 'unable to decode header'}, 401

            except Exception as e:
                logging.error("Invalid token: %s", str(e))
                return {'error': 'invalid token'}, 403

            # if we made it this far, we can continue with the main function
        else:
            logging.info("invalid token or no token provided")
            response_body = {'error': 'invalid token/not authorized'}
            return response_body, 401
        logging.info("access_token validated: %s", str(access_token))

    return wrapper_validate_access

    # def wrapper(view_func):
    #     @wraps(view_func)
    #     def decorated(*args, **kwargs):
    #         token = None
    #         if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
    #             token = request.headers['Authorization'].split(None, 1)[
    #                 1].strip()
    #         if 'access_token' in request.form:
    #             token = request.form['access_token']
    #         elif 'access_token' in request.args:
    #             token = request.args['access_token']

    #         validity = self.validate_token(token, scopes_required)
    #         if (validity is True) or (not require_token):
    #             return view_func(*args, **kwargs)
    #         else:
    #             response_body = {'error': 'invalid_token',
    #                              'error_description': validity}
    #             if render_errors:
    #                 response_body = json.dumps(response_body)
    #             return response_body, 401, {'WWW-Authenticate': 'Bearer'}
    #     return decorated
    # return wrapper
