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
from flask_session import Session
from flask import Flask, request, jsonify, session
from flask import make_response, current_app
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

# initializes app
app = Flask(__name__)
SESSION_TYPE = "redis"
PERMANENT_SESSSION_LIFETIME = 1800
app.config.update(SECRET_KEY =  os.urandom(24))
app.config.from_object(__name__)
Session(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#cors = CORS(app, resources={r"/login/.*": {"origins": "*"}})
#cors = CORS(app, resources={r"/login": {"origins": "*"}})
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

#For login 
LOGIN = Flask(__name__)

# initializes database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    live = db.Column(db.Boolean, nullable=False)


    def __init__(self,username, name,live):
        self.username = username
        self.name = name
        self.live = live

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
        fields = ('id','username', 'name','live')

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

#START STREAM FUNCTIONS---------------------------------------------------------------------
@app.route('/stream', methods = ['GET','POST'])
def get_stream():
    username = request.args.get("username", default=flask.session["username"],type=str)
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

@app.route('/all', methods = ['GET'])
def get_stream():
    streamers = []
    query = Users.query.filter_by(live=True).all()
    for user in query:
        streamers.append({
            'username': user.username,
            'name' : user.name
        })
    return jsonify(streamers=streamers)


#START USER FUNCTIONS---------------------------------------------------------------------
# Gettings a single stream


# login/add user to database
@app.route("/login", methods = ['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():
    # dont want to make a new user each time front end checks if we are logged in
    # only when we log in (POST) AND when the user is not already in our database
    if flask.session.get('logged_in') and flask.session['loggedin']:
        return jsonify(
            username = flask.session['username'],
            name = flask.session['name'],
            loggedin = flask.session['loggedin']
        )
    if flask.request.method == 'POST':
        flask.session['token'] = request.args.get("token", default="",type=str)
        flask.session['loggedin'] = True
        
        # defining a params dict for the parameters to be sent to the API 
        client_id = "hgzp49atoti7g7fzd9v4pkego3i7ae"
        data = {
            "Client-ID" : client_id,
            "Authorization" : "OAuth "+app.session['token']
        } 

        # sending GET request and saving the response as response object 
        r_user_info = requests.get(url = "https://api.twitch.tv/kraken/user", data=data) 
        return_data = json.loads(r_user_info.text)
        username = return_data['display_name']
        name = return_data['name']

        # get username
        flask.session['username'] = username
        flask.session['name'] = name
        
        # check if user is in database
        user = Users.query.filter_by(username=app.session['username']).first()

        #if it is not found
        if user is None:
            new_user = Users(username,name)
            db.session.add(new_user)
            db.session.commit()
        return jsonify(
            username = flask.session['username'],
            name = flask.session['name'],
            loggedin = flask.session['loggedin']
        )
    return jsonify(
        loggedin = False
    )


#END USER FUNCTIONS---------------------------------------------------------------------

#START TEST FUNCTIONS-------------------------------------------------------------------
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"test": "working"})
#END TEST FUNCTIONS---------------------------------------------------------------------


