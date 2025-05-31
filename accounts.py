import base64

from flask import Blueprint, session, redirect, request, jsonify, render_template, make_response

from db import get_db
from login import login_required

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    username =base64.b64decode( data['username'])
    password = base64.b64decode(data['password'])
    passphrase = base64.b64decode(data['passphrase'])
    public_key = data['public_key']
    db = get_db()
    result =db.execute("SELECT * FROM users WHERE username_hash = ?", (username,)).fetchone()
    if result is not None:
        return jsonify({"message": "Username is already in Use"}), 401

    db.execute("INSERT INTO users (username_hash, password_hash, passphrase_hash, pubkey) VALUES (?,?,?,?)",(username,password,passphrase,public_key))
    db.commit()
    return jsonify({"message": "Account created successfully"}), 200

@accounts_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    token_hex = request.cookies.get("auth_token")
    if not token_hex:
        return {"message": "No token found"}, 400

    try:
        token = bytes.fromhex(token_hex)
    except ValueError:
        return {"message": "Invalid token"}, 400

    db = get_db()
    db.execute("DELETE FROM cookies WHERE cookie = ?", (token,))
    db.commit()

    # Clear cookie on client side
    response = make_response({"message": "Logged out"})
    response.set_cookie("auth_token", '', expires=0)
    return response



@accounts_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@accounts_bp.route("/friends", methods=["GET"])
@login_required
def friends():
    return "TODO"