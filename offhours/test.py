"""Off Hours REST API."""
import flask
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import requests
import sqlite3
from sqlite3 import Error

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

def create_connection(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    
def create_project(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO projects(name,begin_date,end_date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    return cur.lastrowid

def create_task(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid

def main():
    database = r"C:/Users/lewjs/OneDrive/Documents/Summer 2020/OffHours/sql/data.sql"

    # create a database connection
    conn = create_connection(database)
    with conn:
        # create a new project
        project = ('Cool App with SQLite & Python', '2015-01-01', '2015-01-30');
        project_id = create_project(conn, project)

        # tasks
        task_1 = ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02')
        task_2 = ('Confirm with user about the top requirements', 1, 1, project_id, '2015-01-03', '2015-01-05')

        # create tasks
        create_task(conn, task_1)
        create_task(conn, task_2)

    
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
        main()
        return test_data; 

api.add_resource(streamData, "/test")

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    offhours.run(debug=True)
    offhours.run(HOST, PORT)