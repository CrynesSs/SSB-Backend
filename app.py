import os

from flask import Flask, render_template, request, jsonify, g, current_app

import accounts
import rooms
import util
from db import init_app, init_db, get_db  # import from db.py
from login import login_bp

app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_NAME"] = "auth_token"


app.register_blueprint(login_bp)
app.register_blueprint(accounts.accounts_bp)
app.register_blueprint(util.util_bp)
app.register_blueprint(rooms.rooms_bp)

app.config['DATABASE'] = os.path.join(app.instance_path, 'your_database.db')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Register database functions
init_app(app)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('home.html', title='Home')

@app.route('/about')
def about():
    return "About"


if __name__ == '__main__':
    app.run()
