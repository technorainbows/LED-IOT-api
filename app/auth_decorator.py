"""Authentication wrapper."""


import json
# import time
from functools import wraps
from flask import Flask, request, make_response, jsonify
import jwt
from jwt.algorithms import RSAAlgorithm, HMACAlgorithm, get_default_algorithms


with open('client_secrets.json', 'r') as myfile:
    data=myfile.read()

# parse client secrets file
data = json.loads(data)
client_secrets = data['web']

def validate_access(func):
    """Authenticate user."""
    @wraps(func)
    def wrapper_validate_access(*args, **kwargs):
        """Validate access."""
        # decode and verify header
        # for i in args:
        #     print("args:", i.value)
        # print("in wrapper")
        # print("request: ", request.headers)
        access_token = None
        
        # access_token = "eyJraWQiOiJYSlpsWnhmUVVUQkVxc2RpeUFXUWNSTWJQU3V6b0V2MVF0SUloVVdCbXV3IiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULnY4X0pfV1VwaVdfNWpYdHVqNUNRc3BNMFkwVEd0cjZlc3pvQy1NWUhwaTAiLCJpc3MiOiJodHRwczovL2Rldi02MzU2MjMub2t0YS5jb20vb2F1dGgyL2RlZmF1bHQiLCJhdWQiOiJhcGk6Ly9kZWZhdWx0IiwiaWF0IjoxNTgxNTY4NjUxLCJleHAiOjE1ODE2NTUwNTEsImNpZCI6IjBvYTE1MTh4d29Nb2Fld0Y2NHg2IiwidWlkIjoiMDB1MTM3MnNtRjc3T0FNTFM0eDYiLCJzY3AiOlsib3BlbmlkIiwiZW1haWwiXSwic3ViIjoiaUBhc2hsZXluZXd0b24ubmV0In0.HBX9hWiY6klE5i-1JMfxIEYrJrtOCvK12-K0CWUIJmv3uO7NtMoNm5h4SjvtwHifDxDNLWqm2-tBATBkoMgYyxg8rkrdu1waPn3GmGgQjt6eCtCyc-BE_gydsulugJ161NhxaeGxjIZscpNprNH3UIKWX4sEMX5eeJVC5JMyEqf02D1Xybxdvo-DOOYDqBO-SKtOB83y-y1pPlxRPpfKfY5JHSTI8BUKZf4AoRySevfF0SgDb7qg7ibg4Lral0Fa7tenduOBuNauFQ29Wn1Umo7C3kXRA7jw7c1nLA35EsuO9ijyuAO2v4eYMefnBSbbTk1l7uQL3ZJ4Jvyfx8Ue2w"
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            access_token = request.headers['Authorization'].split(None, 1)[1].strip()
            # print("token found: ", access_token)

            header = jwt.get_unverified_header(access_token)
            # print("unverified header: ", header)
            
            # if header validated, then decode/check claims
            # assert(header['kid'] == kid)
            try:
                claims = jwt.decode(access_token, client_secrets['client_secret'], verify=False)
                if (claims['cid'] == client_secrets['cid']) and (claims['aud'] == client_secrets['aud']):
                    print("token validated!!")
                    
                    if claims['sub'] in client_secrets['allowed_users']:
                        # print("user permitted! - ", claims['sub'])
                        return func(*args, **kwargs)
                    else:
                        print("user not allowed")
                        return make_response({'error': 'user not allowed'}, 403)
            except Exception as e:
                print("Invalid token: ", str(e))
                return make_response({'error': 'invalid token'}, 403)
            # if we made it this far, we can continue with the main function     
        # else:
        #     response_body = {'error': 'invalid token'}
        #     return response_body, 401

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
