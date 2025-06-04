import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, g, current_app

import accounts
import rooms
import util
from data_handler import data_handler
from db import init_app, init_db, get_db  # import from db.py
from login import login_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_NAME"] = "auth_token"
app.config['DATABASE'] = os.path.join(app.instance_path, 'your_database.db')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024

app.register_blueprint(login_bp)
app.register_blueprint(accounts.accounts_bp)
app.register_blueprint(util.util_bp)
app.register_blueprint(rooms.rooms_bp)
app.register_blueprint(data_handler)

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Register database functions
init_app(app)


if __name__ == '__main__':
    app.run()
