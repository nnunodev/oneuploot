import os
import bcrypt
from os import path
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

if path.exists("env.py"):
    import env

app = Flask(__name__)

# DB settings

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# route for homepage


@app.route('/')
def index():
    return render_template('index.html')

# route to login page


@app.route('/login')
def login():
    return render_template('login.html')
