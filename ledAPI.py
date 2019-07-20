#!/usr/bin/env python


from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
api = Api(app, version='0.1', title='LED API',
     description='A simple LED IOT API',
)

ledState = [False]

@api.route('/light')
class Light(Resource):
    '''Returns ledState (true or false)'''
    def get(self):
        return jsonify({'ledsState': ledState[0]}), 201

@api.route('/light/<string:state>')
@api.doc(params={'state':'true or false'})
class States(Resource):
    '''Changes ledState to on or off (true or false)'''
    def post(self, state):
        if (state=="true"):
            ledState[0] = True
            return  200
        elif (state=="false"):
            ledState[0] = False
            return  200
        else:
            # return 400
            api.abort(404, message="{} not found".format(state))

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
 