#!/usr/bin/env python


from flask import Flask
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
api = Api(app, version='0.1', title='LED API',
     description='A simple LED IOT API',
)

ledState = [False]

@api.route('/light')
class Light(Resource):
    def get(self):
        return ledState[0]

@api.route('/light/<string:state>')
class States(Resource):
    def post(self, state):
        if (state=="true"):
            ledState[0] = True
            return 200
        elif (state=="false"):
            ledState[0] = False
            return 200
        else:
            return 400
        
if __name__ == '__main__':
    app.run(debug=True)
 