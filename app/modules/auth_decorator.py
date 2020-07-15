"""Authentication wrapper."""

import os
import json
import urllib.request
from functools import wraps
import logging
import logging.config
from flask import Flask, request, make_response, jsonify
import jwt
from jwt.exceptions import DecodeError
from jwt.algorithms import RSAAlgorithm

# Set up simple logging.
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)
DEFAULT_LOGGING = logging.DEBUG

# Get LOG_LEVEL from environment if set, otherwise set to default
if 'LOG_LEVEL' not in os.environ:
    logging.warning("LOG_LEVEL not set, using default: %s", DEFAULT_LOGGING)
    LOG_LEVEL = DEFAULT_LOGGING
else:
    # Check if env variable correponds to logging level word or number.
    try:
        # getattr(logging, os.environ['LOG_LEVEL'].upper())
        LOG_LEVEL = getattr(logging, os.environ['LOG_LEVEL'].upper())
        logging.info("LOG_LEVEL set to: %s", LOG_LEVEL)

    except AttributeError:
        TEMP_LEVEL = logging.getLevelName(int(os.environ['LOG_LEVEL']))
        logging.info("temp_level got from env: %s", TEMP_LEVEL)

        if not TEMP_LEVEL.startswith('Level'):
            LOG_LEVEL = TEMP_LEVEL
            logging.info("INT LOG_LEVEL set to: %s", LOG_LEVEL)
        else:
            LOG_LEVEL = logging.WARNING
            logging.warning(
                "Incorrect LOG_LEVEL provided (%s). Setting to WARNING.", TEMP_LEVEL)
    except Exception:
        logging.error(
            "Error with LOG_LEVEL provided. Using default:  %s", DEFAULT_LOGGING)
        LOG_LEVEL = DEFAULT_LOGGING

logging.getLogger().setLevel(LOG_LEVEL)

with open('./client_secrets.json', 'r') as myfile:
    DATA = myfile.read()

# parse client secrets file
DATA = json.loads(DATA)
CLIENT_SECRETS = DATA['web']
logging.info("CLIENT_SECRETS loaded: %s", str(CLIENT_SECRETS))
web_key = urllib.request.urlopen(
    CLIENT_SECRETS['keys_uri']).read().decode()
json_keys = json.loads(web_key)
logging.info("**********************json_key = %s", str(json_keys['keys'][0]))


def validate_access(func):
    """Authenticate user."""
    @wraps(func)
    def wrapper_validate_access(*args, **kwargs):
        """Validate access."""
        # decode and verify header
        logging.info("in validate_access wrapper")
        access_token = None

        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            access_token = request.headers['Authorization'].split(None, 1)[
                1].strip()
            logging.info("token found: %s", access_token)

            try:

                header = jwt.get_unverified_header(access_token)
                logging.info("unverified header: %s", header['kid'])
                if json_keys['keys'][0]['kid'] == header['kid']:
                    key = json.dumps(json_keys['keys'][0])
                    logging.info("key #1 found")
                elif json_keys['keys'][0]['kid'] == header['kid']:
                    key = json.dumps(json_keys['keys'][1])
                    logging.info("key #2 found")
                else:
                    # print("header doesn't match any kids: ", header['kid'])
                    logging.info("invalid header/no matching key found")
                    response_body = {
                        'message': 'please log-in/provide correct authentication token'}
                    return response_body, 401

                # if header validated, then decode/check claims
                try:
                    public_key = RSAAlgorithm.from_jwk(
                        key)
                    claims = jwt.decode(
                        access_token, public_key, audience=CLIENT_SECRETS['aud'], algorithms='RS256')

                    if (claims['cid'] == CLIENT_SECRETS['cid']) and (claims['aud'] == CLIENT_SECRETS['aud']):
                        logging.info("token validated!!")

                        if claims['sub'] in CLIENT_SECRETS['allowed_users']:
                            logging.info("user permitted! - %s", claims['sub'])
                            return func(*args, **kwargs)
                        else:
                            logging.warn("user not allowed")
                            return make_response({'message': 'user not allowed'}, 403)
                    logging.error("claims not validated")

                except ValueError as error:
                    logging.error("***ERROR VALIDATING CLAIMS")
                    raise

            except ValueError:
                logging.error("***********unable to decode header")
                # raise
                return {'ValueError': 'unable to decode header'}, 401

            except DecodeError as e:
                logging.error("DecodeError: %s, ", str(e))
                response_body = {
                    'message': 'invalid login/token - please try again'}
                return response_body, 403

            except Exception as e:
                logging.error("Invalid token: %s", str(e))
                raise
                # return {'error': 'invalid token'}, 403

            # if we made it this far, we can continue with the main function
        else:
            logging.info("invalid token or no token provided")
            response_body = {
                'message': 'please log-in/provide authentication token'}
            # return jwt.exceptions.InvalidTokenError
            return response_body, 401
            # raise
        logging.info("access_token validated: %s", str(access_token))
        return func(*args, **kwargs)
    return wrapper_validate_access
