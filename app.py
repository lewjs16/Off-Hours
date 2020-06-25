import os
import json
import requests
import flask
import flask_cors
import flask_sqlalchemy
import flask_marshmallow
import datetime
from flask import Flask, request, jsonify, session
from flask import make_response, current_app
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

# initializes app
app = Flask(__name__)
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
class Subjects(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    subject = db.Column(db.String(80),nullable=False)

    def __init__(self,id,subject):
        self.id = id
        self.subject = subject

class Streams(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    subject = db.Column(db.String(80),db.ForeignKey('subjects.id'),nullable=False)
    ownerid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    vidnum = db.Column(db.Integer,nullable=True)

    def __init__(self,title,subject,ownerid):
        self.title=title
        self.subject=subject
        self.ownerid=ownerid

class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    name = db.Column(db.String(80),nullable=False)
    token = db.Column(db.Integer,nullable=True)
    time = db.Column(db.Integer,nullable=True)
    loggedin = db.Column(db.Boolean, nullable=False)

    def __init__(self,username, name):
        self.username = username
        self.name = name

class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    streamid = db.Column(db.Integer,db.ForeignKey('streams.id'),nullable=False)
    userid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    offervalue = db.Column(db.Integer,nullable=False)
    message = db.Column(db.Text,nullable=True)
    image = db.Column(db.String(80),nullable=True)
    accepted = db.Column(db.Boolean,default=False,nullable=False)
    completed = db.Column(db.Boolean,default=False,nullable=False)
    time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    def __init__(self,streamid,userid,message,image):
        self.streamid = streamid
        self.userid = userid
        if (message):
            self.message = message
        if (image):
            self.image = image

#Schema 
class Subjects_Schema(ma.Schema):
    class Meta:
        fields = ('id','subject')

class Streams_Schema(ma.Schema):
    class Meta:
        fields = ('id','title', 'subject', 'ownerid')

class User_Schema(ma.Schema):
    class Meta: 
        fields = ('id','username', 'name')

class Questions_Schema(ma.Schema):
    class Meta: 
        fields = ('id','streamid','userid', 'message', 'image')


#Init Schema
streams_schema_reg = Streams_Schema()
user_schema_reg = User_Schema()
questions_schema_reg = Questions_Schema()
subjects_schema_reg = Subjects_Schema()

streams_schema_multi = Streams_Schema(many=True)
user_schema_multi = User_Schema(many=True)
questions_schema_multi = Questions_Schema(many=True)
subjects_schema_multi = Subjects_Schema(many = True)

streams_schema_single = Streams_Schema(many = False)
user_schema_single = User_Schema(many=False)
questions_schema_single = Questions_Schema(many=False)
subjects_schema_single = Subjects_Schema(many = False)

#START STREAM FUNCTIONS---------------------------------------------------------------------

#Adding a stream
@app.route('/addStream', methods = ['POST'])
def add_stream():
    title = request.json['title']
    subject = request.json['subject']
    ownerid = request.json['ownerid']

    new_stream = Streams(title, subject, ownerid)

    db.session.add(new_stream)
    db.session.commit()

    return streams_schema_reg.jsonify(new_stream)

# Getting all streams
@app.route('/Streams', methods = ['GET'])
def get_streams():
    all_streams = Streams.query.all()
    #serialize the queryset
    result = streams_schema_multi.dump(all_streams)
    return jsonify(result)

# Gettings a single stream
@app.route('/Stream/<id>', methods = ['GET'])
def get_stream(id):
     stream = Streams.query.get(id)


     result = streams_schema_single.dump(stream)
     return jsonify(result)

# Update single stream
@app.route('/StreamUpdate/<id>', methods = ['PUT'])
def update_stream(id):
    title = request.json['title']
    subject = request.json['subject']
    ownerid = request.json['ownerid']

    update_stream = Streams.query.get(id)

    update_stream.title = title
    update_stream.subject = subject
    update_stream.ownerid = ownerid

    db.session.commit()

    return streams_schema_single.jsonify(update_stream)

# Delete stream
@app.route('/StreamDelete/<id>', methods = ['DELETE'])
def delete_stream(id):
    stream = Streams.query.get(id)
    db.session.delete(stream)
    db.session.commit()

    return streams_schema_reg.jsonify(stream)

#END STREAM FUNCTIONS---------------------------------------------------------------------

#START USER FUNCTIONS---------------------------------------------------------------------

#Check login
@app.route('/login_check/<id>', methods = ['POST'])
def login_check(id):
    user = Users.query.get(id)
    if user is None:
        return ({"username": "Not Available", "logid": False})

    if user.time is 0:
        return ({"username": user.username, "logid": False})
    else:
        return ({"username": user.username, "logid": True})

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
      	# get tokenfrom Twitch API
        client_id = "hgzp49atoti7g7fzd9v4pkego3i7ae"
        client_secret = "yejdl550a2zan6t4bb0mc3k8xbsvbz"
        auth_code = flask.request.args.get("code", default="",type=str)
        #auth_code = "32q29ae62768cu7658a4dflvocp2m4"
        redirect_uri = "https://offhours.herokuapp.com/login/"
        data = requests.post("https://id.twitch.tv/oauth2/token?client_id="+client_id+"&client_secret=" + client_secret+"&code="+auth_code+"&grant_type=authorization_code&redirect_uri="+redirect_uri)
        
        # store token and other info
        return jsonify(json.loads(data.text))
        token_data = json.loads(data.text)
        flask.session['token'] = token_data['access_token']
        flask.session['refresh_token'] = token_data['refresh_token']
        flask.session['expiration_date'] = datetime.now() +  datetime.timedelta(0,token_data['expires_in'])
        flask.session['loggedin'] = True
        
         # defining a params dict for the parameters to be sent to the API 
        PARAMS = {
            "Client-ID" : client_id,
            "Authorization" : "OAuth "+app.session['token']
        } 

        # sending GET request and saving the response as response object 
        r_user_info = requests.get(url = "https://api.twitch.tv/kraken/user", params = PARAMS) 
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
        loggedin = False
    )


#END USER FUNCTIONS---------------------------------------------------------------------

#START TEST FUNCTIONS-------------------------------------------------------------------
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"test": "working"})
#END TEST FUNCTIONS---------------------------------------------------------------------


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

