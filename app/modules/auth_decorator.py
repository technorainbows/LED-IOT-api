"""Authentication wrapper."""

import os
import json
from functools import wraps
import logging
import logging.config
from flask import Flask, request, make_response, jsonify
import jwt

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

with open('./CLIENT_SECRETS.json', 'r') as myfile:
    DATA = myfile.read()

# parse client secrets file
DATA = json.loads(DATA)
CLIENT_SECRETS = DATA['web']


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
                logging.info("unverified header: %s", header)

                # if header validated, then decode/check claims
                claims = jwt.decode(
                    access_token, CLIENT_SECRETS['client_secret'], verify=False)

                if (claims['cid'] == CLIENT_SECRETS['cid']) and (claims['aud'] == CLIENT_SECRETS['aud']):
                    logging.info("token validated!!")

                    if claims['sub'] in CLIENT_SECRETS['allowed_users']:
                        logging.info("user permitted! - %s", claims['sub'])
                        return func(*args, **kwargs)
                    else:
                        logging.warn("user not allowed")
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
