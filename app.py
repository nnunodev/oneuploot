import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

# DB settings

app.config["MONGO_DBNAME"] = os.getenv("MONGO_DBNAME")
app.config["FLASK_DEBUG"]  = os.getenv("FLASK_DEBUG")
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# route for homepage


@app.route('/')
def index():
    return render_template('index.html')

# route to user to login


@app.route('/login', methods=['POST'])
def login():
    # connect users to users db.
    users = mongo.db.users
    # find user in the db
    login_user = users.find_one({'name': request.form['username']})
    # if user exists compare password to db
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    else:
        #if it's incorrect return error message
        error = 'Invalid username/password'
        return render_template('login.html', error_login=error)

# route for the login page


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')
