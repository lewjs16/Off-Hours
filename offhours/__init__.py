"""Off Hours REST API."""
import flask
from flask import Flask, jsonify
from flask_restful import Resource
import requests

offhours = Flask(__name__)

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

@offhours.route('/login', methods = ['POST', 'GET'])
def getAccess_account(){
    clientID = "glsmk1f8nj211k9v1r916xbsgqnuq4"
    secret = "fzisu9q67fhgx6wpg1yqd9fia52502"
    r_token = requests.post("https://id.twitch.tv/oauth2/token",
    {"client_id" : clientID, "client_secret" :  secret,"grant_type" :'client_credentials', "redirect_uri" :'http://localhost'})

    r_login = requests.get("https://id.twitch.tv/oauth2/authorize",
    {"client_id": clientID,"redirect_uri" :'http://localhost', "response_type":'code', "scope": 'user_read' })

    r_code = r_login.text; 
    print(r.text)
}

@offhours.route('/subject:streamers', methods = ['POST'])
def getSubjectStreamers(){
    return test_data; 
}