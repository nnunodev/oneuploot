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
app.config["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG")
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
app.config["SECRET_KEY"] = "mysecret"
mongo = PyMongo(app)

# route for homepage


@app.route('/')
def index():
    if 'username' in session:
        user = session['username']
        return render_template('index.html', user=user)
    else:
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
            # if it's incorrect return error message
            error = 'Invalid username/password'
            return render_template('login.html', error_login=error)
    else:
        error = 'Invalid username/password'
        return render_template('login.html', error_login=error)


# route for the login page
@app.route('/login_page')
def login_page():
    return render_template('login.html')


# route to register user
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})
        # check if user is already registered
        if existing_user is None:
            # create a hash for pwd user  submitted
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'),
                bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            # error message if the user already exists
            error = 'Username already exists'
            return render_template('signup.html', error_register=error)
    else:
        return render_template('signup.html')


# route for logout users
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# route for user profile
@app.route('/<username>')
def profile(username):
    if 'username' in session:
        user = session['username']
        return render_template('profile.html', games=mongo.db.games.find(), genres=mongo.db.genres.find(), platforms=mongo.db.platforms.find(), user=user)


# search route for platform
@app.route('/get_search/<search>')
def get_search(search):
    # check if user is logged in
    if 'username' in session:
        user = session['username']
        # search for platforms
        plat_list = list(mongo.db.games.find({"platform_name": search}))
        return render_template("results.html", user=user, platforms=plat_list, games=mongo.db.games.find(), genres=mongo.db.genres.find())
    else:
        return redirect(url_for('index'))


# search route for game genre search
@app.route('/search_genre/<genre>')
def search_genre(genre):
    # checks if user is logged in
    if 'username' in session:
        user = session['username']
        # search for genre name user chose in db
        genre_list = list(mongo.db.games.find({"genre_name": genre}))
        return render_template("results_genre.html", user=user, games=mongo.db.games.find(), genres=genre_list)
    else:
        return redirect(url_for('index'))


# route for adding games page
@app.route('/add_games')
def add_games():
    # checks if user is logged
    if 'username' in session:
        user = session['username']
        return render_template("addgame.html", games=mongo.db.games.find(), genres=mongo.db.genres.find(), platforms=mongo.db.platforms.find(), user=user)
    else:
        return redirect(url_for('index'))


# route to add the games form data in the db.
@app.route('/insert_game', methods=['POST'])
def insert_game():
    user = session['username']
    games = mongo.db.games
    games.insert_one({
        'user': session['username'],
        'game_name': request.form.get('game_name'),
        'game_image': request.form.get('game_image'),
        'game_condition': request.form.get('game_condition'),
        'pickup_date': request.form.get('pickup_date'),
        'platform_name': request.form.get('platform_name'),
        'genre_name': request.form.get('genre_name'),
        'game_condition': request.form.get('game_condition'),
        'game_store': request.form.get('game_store'),
        'game_price': request.form.get('game_price'),
        'game_value': request.form.get('game_value'),
    })
    return redirect(url_for('profile', username=user))


# route to enable the user to Edit games from their list
@app.route('/edit_game/<game_id>')
def edit_game(game_id):
    user = session['username']
    game_edit = mongo.db.games.find_one({"_id": ObjectId(game_id)})
    genres = mongo.db.genres.find()
    platforms = mongo.db.platforms.find()
    return render_template('editgame.html', user=user, game=game_edit, genre=genres, plat=platforms)


# route to update games form data in the db
@app.route('/update_game/<game_id>', methods=["POST"])
def update_game(game_id):
    user = session['username']
    games = mongo.db.games
    games.update({'_id': ObjectId(game_id)},
                 {
        'user': session['username'],
        'game_name': request.form.get('game_name'),
        'game_image': request.form.get('game_image'),
        'game_condition': request.form.get('game_condition'),
        'pickup_date': request.form.get('pickup_date'),
        'platform_name': request.form.get('platform_name'),
        'genre_name': request.form.get('genre_name'),
        'game_condition': request.form.get('game_condition'),
        'game_store': request.form.get('game_store'),
        'game_price': request.form.get('game_price'),
        'game_value': request.form.get('game_value'),
    })
    return redirect(url_for('profile', username=user))


# route to enable the user to delete the game from the db
@app.route('/delete_task/<game_id>')
def delete_game(game_id):
    user = session['username']
    mongo.db.games.remove({'_id': ObjectId(game_id)})
    return redirect(url_for('profile', username=user))
