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
    streamimg = db.Column(db.String(80),nullable=False)
    vidnum = db.Column(db.Integer,nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer,db.ForeignKey('streams.ownerid'),primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    userimg = db.Column(db.String(80),nullable=False)

class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    streamid = db.Column(db.Integer,db.ForeignKey('streams.id'),nullable=False)
    message = db.Column(db.Text,nullable=True)
    image = db.Column(db.String(80),nullable=True)
    accepted = db.Column(db.Boolean,default=False,nullable=False)
    completed = db.Column(db.Boolean,default=False,nullable=False)
    time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)


@app.route('/',methods=['GET'])
def get():
    return jsonify({'msg':'Hellow World'})

if __name__ == '__main__':
    app.run(debug=True)

