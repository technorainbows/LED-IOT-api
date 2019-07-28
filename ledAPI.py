#!/usr/bin/env python


from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, cors


app = Flask(__name__)
api = Api(app, version='0.1', title='LED API',
     description='A simple LED IOT API',
)

ledState = [False]


@api.route('/light')
class Light(Resource):
    '''Returns ledState (true or false)'''
    @cors.crossdomain(origin='*', headers='content-type')
    def get(self):
        print('get request: ', ledState[0])
        return jsonify({'ledState': ledState[0]})

@api.route('/light/<string:stateType>/<string:state>')
@api.doc(params={'state':'true or false'})
class States(Resource):
    '''Changes ledState to on or off (true or false)'''
    @cors.crossdomain(origin='*', headers=['content-type'], methods=['post'])
    def post(self, stateType, state):
        print("[post request: " + state )
        if (state=="true"):
            ledState[0] = True
            # print("[post request: " + state )
            return jsonify({'ledState': ledState[0]})
        elif (state=="false"):
            ledState[0] = False

            return jsonify({'ledState': ledState[0]})
        else:
            # return 400
            api.abort(404, message="{} not found".format(state))

@app.errorhandler(404)
def not_found(error):
    return (jsonify({'error': 'Not found'}), 404)

# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

# @app.before_request
# def allow_origin(response):
#     response.headers['Access-Control-Allow-Origin']='*'
#     return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 