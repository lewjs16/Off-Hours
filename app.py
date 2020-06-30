import os
import json
import requests
import flask
import flask_cors
import flask_sqlalchemy
import flask_marshmallow
import flask_session
import datetime
import redis
import simplejson
import pusher

from flask import Flask, request, jsonify, session,make_response, current_app, render_template, json
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from pusher import pusher
    
# initializes app
app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'

# initializes database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SECRET_KEY'] = b'6hc/_gsh,./;2ZZx3c6_s,1//'

app.config.from_object(__name__)

CORS(app)

 # configure pusher object
pusher = pusher.Pusher(
app_id="1027801",
key="3aceae7853d07b617f87",
secret="d5c458d63bcf29605608",
cluster="us2",
ssl=True)

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)


#Classes 
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(80), nullable = False)
    live = db.Column(db.Boolean, nullable=False)


    def __init__(self,username, name,live, email):
        self.username = username
        self.name = name
        self.live = live
        self.email = email

class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    message = db.Column(db.Text,nullable=True)
    completed = db.Column(db.Boolean,default=False,nullable=False)
    time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self,userid,message):
        self.userid = userid
        self.message = message
        self.completed = False

#Schema 
class User_Schema(ma.Schema):
    class Meta: 
        fields = ('id','username', 'name','live', 'email')

class Questions_Schema(ma.Schema):
    class Meta: 
        fields = ('id','userid', 'message')


# Init Schema
user_schema_reg = User_Schema()
questions_schema_reg = Questions_Schema()

user_schema_multi = User_Schema(many=True)
questions_schema_multi = Questions_Schema(many=True)

user_schema_single = User_Schema(many=False)
questions_schema_single = Questions_Schema(many=False)

#START CHAT FUNCTIONS-----------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')
#END CHAT FUNCTIONS-------------------------------------------------------------------------


#START STREAM FUNCTIONS---------------------------------------------------------------------
@app.route('/stream', methods = ['GET','POST'])
def get_stream():
    username = flask.request.args['username']
    user = Users.query.filter_by(username=username).first()
    live = user.live
    
    if flask.request.method == 'POST':
        tmp = request.args.get("live", default="",type=str)
        if(tmp=='true'):
            user.live=True
            live = True
        else:
            user.live=False
            live = False
        db.session.commit()
    return jsonify(
        username = user.username,
        name = user.name,
        isLive = live
    )


#START USER FUNCTIONS---------------------------------------------------------------------
# Gettings a single stream


# login/add user to database
@app.route("/login", methods = ['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():
    # dont want to make a new user each time front end checks if we are logged in
    # only when we log in (POST) AND when the user is not already in our database
    if flask.request.method == 'GET':
        return jsonify(username = session.get('username'))
 

    if flask.request.method == 'POST':
        token = flask.request.args['token']

        # defining a params dict for the parameters to be sent to the API 
        client_id = "hgzp49atoti7g7fzd9v4pkego3i7ae"
        headers = {
            'Accept' : 'application/vnd.twitchtv.v5+json',
            'Client-ID' : client_id,
            'Authorization' : 'OAuth '+ token,
        }

        # sending GET request and saving the response as response object 
        r_user_info = requests.get('https://api.twitch.tv/kraken/user',headers = headers) 

        return_data = json.loads(r_user_info.text)
        username = return_data['display_name']
        name = return_data['name']
        email = return_data['email']

        # get username
        session['username'] = username
        session.modified = True
        
        # check if user is in database
        user = Users.query.filter_by(username= username).first()
        live = False; # Default

        #if it is not found
        if not user:
            new_user = Users(username,name, live, email)
            db.session.add(new_user)
            db.session.commit()
        
        return jsonify(
            username = session.get('username')
        )


#END USER FUNCTIONS---------------------------------------------------------------------

#START TEST FUNCTIONS-------------------------------------------------------------------
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"test": "working"})

@app.route('/test_session')
def test_session():
    res = make_response("Setting a cookie")
    res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)
    return jsonify({"test": "here"})

@app.route('/check_session')
def check_session():
    return jsonify({"username":request.cookies.get('foo') })
    
#END TEST FUNCTIONS---------------------------------------------------------------------


if __name__ == '__main__':
  #db.create_all()
  app.secret_key = "123"
  app.run()