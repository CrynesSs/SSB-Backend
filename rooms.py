from flask import request, render_template, Blueprint, jsonify

from db import get_db
from login import login_required

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

# Shows the rooms this user is a member of
@rooms_bp.route('',methods=['POST'])
@login_required
def rooms():
    data = request.get_json()
    return "TODO"

@rooms_bp.route('/create_room',methods=['POST'])
@login_required
def room():
    data = request.get_json()
    cookie = request.cookies.get("auth_token")
    if not cookie:
        return jsonify("Malformed Request"),401

    db = get_db()
    user = db.execute("")


    return "TODO"

@rooms_bp.route('/delete_room',methods=['POST'])
@login_required
def delete_room():
    data = request.get_json()
    return "TODO"

@rooms_bp.route('/edit_room',methods=['POST'])
@login_required
def edit_room():
    data = request.get_json()
    return "TODO"


