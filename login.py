import base64
import hashlib
import random
from random import randbytes

from flask import render_template, jsonify, request, Blueprint, session, abort, g, make_response, redirect, url_for

from db import get_db
from util import hash_with_salt, generate_salt

login_bp = Blueprint('login', __name__, url_prefix='/login')


@login_bp.route('/salts',methods=['Post'])
def salts():
    try:
       data = request.get_json()
       key = data['public_key']
       db = get_db()
       user = db.execute("SELECT * FROM users WHERE pubkey = ?",(key,)).fetchone()
       if user is None:
           return jsonify({"message": "Invalid username or password or user not found"}), 401
       return jsonify({"username_salt" : user["username_salt"],"password_salt" : user["password_salt"],"passphrase_salt" : user["passphrase_salt"]})
    except Exception as e:
        print(e)
        return jsonify({"message": "Invalid username or password or user not found"}), 401


@login_bp.route('/', methods=['GET'])
def login():
    token = request.cookies.get('auth_token')
    if token is None:
        return render_template('login.html')
    return redirect(url_for('accounts.dashboard'))

@login_bp.route('/', methods=['POST'])
def login_post():
    data = request.get_json()
    token = request.cookies.get('auth_token')
    if token:
        # Optional: you could also verify the token here using your verify_token()
        return jsonify("Already logged in"), 200
    try:
        username = base64.b64decode(data['username'])
        password = base64.b64decode(data['password'])
        passphrase = base64.b64decode(data['passphrase'])
        public_key = data['public_key']
    except KeyError:
        return jsonify(message='Malformed Request'), 400

    db = get_db()
    proto_user = db.execute("SELECT * FROM users WHERE pubkey = ?", (public_key,)).fetchone()
    if proto_user is None:
        return jsonify({"message": "Invalid username or password or user not found"}), 401
    # Get the salts from the Database
    username_salt = proto_user["username_salt"]
    password_salt = proto_user["password_salt"]
    passphrase_salt = proto_user["passphrase_salt"]

    username = hash_with_salt(username.hex(), username_salt)
    password = hash_with_salt(password.hex(), password_salt)
    passphrase = hash_with_salt(passphrase.hex(), passphrase_salt)

    user = db.execute(
        "SELECT * FROM users WHERE username_hash = ? AND password_hash = ? AND passphrase_hash = ?",
        (username, password, passphrase)).fetchone()
    if user is None:
        return jsonify({"message": "Invalid username or password or user not found"}), 401


    data = (base64.b64decode(username) + base64.b64decode(password) + base64.b64decode(passphrase)) + randbytes(32)

    cookie = hashlib.sha256(data).digest()

    db.execute("INSERT INTO cookies (user_id, cookie) VALUES (?,?)", (user['id'], cookie))
    db.commit()

    resp = make_response(jsonify({"message": "Login successful"}))
    resp.set_cookie("auth_token", cookie.hex(), httponly=True, secure=True, samesite="Strict", path="/")

    return resp, 200


def verify_token():
    token_hex = request.cookies.get("auth_token")
    if not token_hex:
        return None

    try:
        token = bytes.fromhex(token_hex)
    except ValueError:
        return None

    db = get_db()
    result = db.execute(
        "SELECT users.id, users.username_hash FROM cookies JOIN users ON cookies.user_id = users.id WHERE cookie = ?",
        (token,)
    ).fetchone()

    if result:
        return {"user_id": result["id"], "username": result["username_hash"]}
    return None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = verify_token()
        if not user:
            return redirect(url_for('login.login', next=request.path))
        g.user = user  # Attach to `g`
        return f(*args, **kwargs)

    return decorated_function
