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
from flask_session import Session
from flask import Flask, request, jsonify, session
from flask import make_response, current_app
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from flask import render_template, json
from pusher import pusher
    
# initializes app
app = Flask(__name__)
#engine = create_engine("sqlite://")
#session_factory = sessionmaker(bind=engine)
#session = flask_scoped_session(session_factory, app)

app.config['CORS_HEADERS'] = 'Content-Type'

# initializes database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')

SESSION_TYPE = 'filesystem'
SECRET_KEY = "hello"
app.config.from_object(__name__)

#cors = CORS(app, resources={r"/login/.*": {"origins": "*"}})
#cors = CORS(app, resources={r"/login": {"origins": "*"}})
Session(app)
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
# class Subjects(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     subject = db.Column(db.String(80),nullable=False)

#     def __init__(self,id,subject):
#         self.id = id
#         self.subject = subject

# class Streams(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     title = db.Column(db.String(80),nullable=False)
#     subject = db.Column(db.String(80),db.ForeignKey('subjects.id'),nullable=False)
#     ownerid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
#     vidnum = db.Column(db.Integer,nullable=True)

#     def __init__(self,title,subject,ownerid):
#         self.title=title
#         self.subject=subject
#         self.ownerid=ownerid

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
    # streamid = db.Column(db.Integer,db.ForeignKey('streams.id'),nullable=False)
    userid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    # offervalue = db.Column(db.Integer,nullable=False)
    message = db.Column(db.Text,nullable=True)
    # image = db.Column(db.String(80),nullable=True)
    # accepted = db.Column(db.Boolean,default=False,nullable=False)
    completed = db.Column(db.Boolean,default=False,nullable=False)
    time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self,userid,message):
        self.userid = userid
        self.message = message
        self.completed = False

#Schema 
# class Subjects_Schema(ma.Schema):
#     class Meta:
#         fields = ('id','subject')

# class Streams_Schema(ma.Schema):
#     class Meta:
#         fields = ('id','title', 'subject', 'ownerid')

class User_Schema(ma.Schema):
    class Meta: 
        fields = ('id','username', 'name','live', 'email')

class Questions_Schema(ma.Schema):
    class Meta: 
        fields = ('id','userid', 'message')


# Init Schema
# streams_schema_reg = Streams_Schema()
user_schema_reg = User_Schema()
questions_schema_reg = Questions_Schema()
# subjects_schema_reg = Subjects_Schema()

# streams_schema_multi = Streams_Schema(many=True)
user_schema_multi = User_Schema(many=True)
questions_schema_multi = Questions_Schema(many=True)
# subjects_schema_multi = Subjects_Schema(many = True)

# streams_schema_single = Streams_Schema(many = False)
user_schema_single = User_Schema(many=False)
questions_schema_single = Questions_Schema(many=False)
# subjects_schema_single = Subjects_Schema(many = False)

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
        # return jsonify(
        #     username = flask.session['username'],
        #     name = flask.session['name'],
        #     loggedin = flask.session['loggedin'],
        #     test = "got here"
        # )
        if flask.session.get('username'):
            return jsonify(
            username = flask.session['username']
            ) 
        else:
            return jsonify(
            username = "Not logged in"
            )
    
    # if 'loggedin' in session and session['loggedin']:
    #     return jsonify(
    #         username = session['username'],
    #         name = session['name'],
    #         loggedin = session['loggedin'],
    #         test = "got here"
    #     )
    if flask.request.method == 'POST':
        #flask.session['token'] = flask.request.args['token']
        token = flask.request.args['token']
        #session['token'] = '9dc9rumb7sf6fx32quyyh2tiuz62xw'
        #flask.session['loggedin'] = True
        
        # defining a params dict for the parameters to be sent to the API 
        client_id = "hgzp49atoti7g7fzd9v4pkego3i7ae"
        headers = {
            'Accept' : 'application/vnd.twitchtv.v5+json',
            'Client-ID' : client_id,
            'Authorization' : 'OAuth '+ token,
        }

        # sending GET request and saving the response as response object 
        r_user_info = requests.get('https://api.twitch.tv/kraken/user',headers = headers) 

        #assert r_user_info.json() == None
        #assert json.loads(r_user_info.text)== {"display_name":"chinagirl123","_id":"543992639","name":"chinagirl123","type":"user","bio":null,"created_at":"2020-06-15T04:34:42.653308Z","updated_at":"2020-06-26T19:21:20.331875Z","logo":"https://static-cdn.jtvnw.net/user-default-pictures-uv/dbdc9198-def8-11e9-8681-784f43822e80-profile_image-300x300.png","email":"j8rocks@gmail.com","email_verified":true,"partnered":false,"twitter_connected":false,"notifications":{"push":true,"email":true}}
        return_data = json.loads(r_user_info.text)
        username = return_data['display_name']
        name = return_data['name']
        email = return_data['email']
        #username = "test"
        #name = "again"

        # get username
        flask.session['username'] = username
        #flask.session['name'] = name
        
        # check if user is in database
        user = Users.query.filter_by(username= flask.session['username']).first()
        live = False; # Default

        #if it is not found
        if not user:
            new_user = Users(username,name, live, email)
            db.session.add(new_user)
            db.session.commit()
        
        return jsonify(
            username = flask.session['username']
        )
        # return jsonify(
        #     username = flask.session['username'],
        #     name = flask.session['name'],
        #     loggedin = flask.session['loggedin']
        # )
    # if 'username' not in session:
    #     session['username'] = "not working"
    # return jsonify(
    #     test = session['username'],
    #     loggedin = False
    # )


#END USER FUNCTIONS---------------------------------------------------------------------

#START TEST FUNCTIONS-------------------------------------------------------------------
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"test": "working"})

@app.route('/test_session')
def test_session():
    session['name'] = "test session"
    return 'Hello was saved into session[this_one].'

@app.route('/check_session')
def check_session():
    return jsonify({"check session" : session['name']})


#END TEST FUNCTIONS---------------------------------------------------------------------


if __name__ == '__main__':
  #db.create_all()
  app.run(debug = True)