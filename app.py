from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime

# initializes app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# initializes database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

class Streams(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    subject = db.Column(db.String(80),nullable=False)
    ownerid = db.Column(db.Integer,nullable=False)
    streamimg = db.Column(db.String(80),default=True)
    vidnum = db.Column(db.Integer,nullable=True)

    def __init__(self,title,subject,ownerid):
        self.title=title
        self.subject=subject
        self.ownerid=ownerid

class Users(db.Model):
    id = db.Column(db.Integer,db.ForeignKey('streams.ownerid'),primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    userimg = db.Column(db.String(80),nullable=False)

    def __init__(self,username,userimg):
        self.username = username
        self.userimg = userimg

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
class Streams_Schema(ma.Schema):
    class Meta:
        fields = ('id','title', 'subject', 'ownerid')

class User_Schema(ma.Schema):
    class Meta: 
        fields = ('id','username', 'userimg')

class Questions_Schema(ma.Schema):
    class Meta: 
        fields = ('id','streamid','userid', 'message', 'image')


#Init Schema
streams_schema_reg = Streams_Schema()
user_schema_reg = User_Schema()
questions_schema_reg = Questions_Schema()

streams_schema_multi = Streams_Schema(many=True)
user_schema_multi = User_Schema(many=True)
questions_schema_multi = Questions_Schema(many=True)

streams_schema_single = Streams_Schema(many = False)
user_schema_single = User_Schema(many=False)
questions_schema_single = Questions_Schema(many=False)

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
     try:
        stream = Streams.query.get(id)
     except IntegrityError:
        return jsonify({"message": "Stream could not be found."}), 400

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

if __name__ == '__main__':
    app.run(debug=True)

