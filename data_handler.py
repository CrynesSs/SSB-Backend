import os

from flask import request, jsonify, Blueprint

from app import app
from db import get_db
from db_helper import fetch_user_by_cookie
from login import login_required


data_handler = Blueprint('data_handler', __name__, url_prefix='/data')

@data_handler.route("/init_upload")
@login_required
def init_upload():
    cookie = request.cookies.get("auth_token")
    user = fetch_user_by_cookie(cookie)

    # Ensure base folder for user exists
    user_folder = os.path.join(UPLOAD_ROOT, user["username_hash"])
    os.makedirs(user_folder, exist_ok=True)
    return


@data_handler.route("/upload_data", methods=["POST"])
@login_required
def upload_data():
    try:
        file_id = request.form['file_id']
        chunk_index = int(request.form['chunk_index'])
        total_chunks = int(request.form['total_chunks'])
        file = request.files['chunk']
        cookie = request.cookies.get("auth_token")
    except KeyError:
        return jsonify("Malformed request"),401

    db = get_db()
    user = fetch_user_by_cookie(cookie)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Calculate total used storage
    usage = db.execute("SELECT COALESCE(SUM(LENGTH(file_size)), 0) as total FROM user_data_file WHERE uploaded_by = ?", (user["username_hash"],)).fetchone()

    if usage["total"] + len(blob) > user["max_storage_bytes"]:
        return jsonify({"error": "Storage limit exceeded"}), 403

    db.execute(
        "INSERT INTO user_data (recipient_user_id, data) VALUES (?, ?)",
        (user["id"], blob)
    )
    db.commit()

    return jsonify({"status": "data stored"})
