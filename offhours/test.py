"""Off Hours REST API."""
import flask
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import requests

offhours = Flask(__name__)
api = Api(offhours)

test_data = [
    {   
        "subject": "AP Chemistry",
        "streams": [
            {
                "streamer": "Raul Dutta",
            },
            {
                "streamer": "Daniel Zheng"
            }]
    },
    {
        "subject": "EECS 281",
        "streams": [
            {
                "streamer": "Jillian Lew",
            },
            {
                "streamer": "Brandon Zhu"
            }]
    }
]

class login(Resource):
    def get(self):
        clientID = "glsmk1f8nj211k9v1r916xbsgqnuq4"
        secret = "fzisu9q67fhgx6wpg1yqd9fia52502"
        r_token = requests.post("https://id.twitch.tv/oauth2/token",
        {"client_id" : clientID, "client_secret" :  secret,"grant_type" :'client_credentials', "redirect_uri" :'http://localhost'})

        r_login = requests.get("https://id.twitch.tv/oauth2/authorize",
        {"client_id": clientID,"redirect_uri" :'http://localhost', "response_type":'code', "scope": 'user_read' })
        return r_token.text; 

class streamData(Resource):
    def get(self):
        return test_data; 

api.add_resource(login, "/test")

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
   
    offhours.run(debug=True)
    offhours.run(HOST, PORT)