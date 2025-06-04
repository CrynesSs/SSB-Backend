import os

from flask import request, jsonify, Blueprint

from db import get_db
from db_helper import fetch_user_by_cookie
from login import login_required

data_handler = Blueprint('data_handler', __name__, url_prefix='/data')

@data_handler.route("/init_upload")
@login_required
def init_upload():
    # Handling the getting of the File Data
    data = request.get_json()
    try:
        filename = data['filename']
        total_size = data['total_size']
        total_chunks = data['total_chunks']
    except KeyError:
        return jsonify({'message': 'Missing required parameter'}), 400

    cookie = request.cookies.get("auth_token")
    user = fetch_user_by_cookie(cookie)
    if user is None:
        return jsonify({'message': 'Invalid auth token'}), 401

    # Ensure User can upload files
    db = get_db()
    if db.execute("SELECT * FROM uploads WHERE uploaded_by = ?", user["username_hash"]) is not None:
        return jsonify({'message': 'User already uploading, cancel current upload first'}), 409
    # Calculate total used storage
    usage = db.execute("SELECT COALESCE(SUM(LENGTH(file_size)), 0) as total FROM user_data_file WHERE uploaded_by = ?", (user["username_hash"],)).fetchone()
    if user["max_storage_bytes"] < usage["total"] + total_size:
        return jsonify({'message': 'Upload is too big'}), 400

    # Ensure base folder for user exists
    user_folder = os.path.join(os.getenv("UPLOAD_ROOT"), user["username_hash"])
    os.makedirs(user_folder, exist_ok=True)
    # Checks is the user is already uploading.

    # Inserts the Upload into the Database and commits it. Sending 200 to User.
    db.execute("INSERT INTO uploads (uploaded_by,file_name, file_size, total_chunks) VALUES (?,?,?,?)",(user["username_hash"],filename, total_size,total_chunks, ))
    db.commit()
    return jsonify({'filename': filename, 'total_size': total_size, 'total_chunks': total_chunks,'message': 'Upload_Initialized'}),200

@data_handler.route("/cancel_upload", methods=['POST'])
@login_required
def cancel_upload():
    data = request.cookies.get("auth_token")
    user = fetch_user_by_cookie(data)
    if user is None:
        return jsonify({'message': 'Invalid auth token'}), 401
    db = get_db()
    result = db.execute("SELECT * FROM uploads WHERE uploaded_by = ?", user["username_hash"]).fetchone()
    if result is None:
        return jsonify({'message': 'User is not currently Uploading'}), 400

    user_folder = os.path.join(os.getenv("UPLOAD_ROOT"), user["username_hash"])
    os.remove(os.path.join(user_folder, result["file_name"]))

    db.execute("DELETE FROM uploads WHERE uploaded_by = ?", user["username_hash"])
    db.commit()
    return jsonify({'message': 'Upload Canceled'}), 200


@data_handler.route("/upload_data", methods=["POST"])
@login_required
def upload_data():
    cookie = request.cookies.get("auth_token")
    try:
        chunk_index = int(request.form['chunk_index'])
        file = request.files['chunk']
    except KeyError:
        return jsonify("Malformed request"),401

    db = get_db()
    user = fetch_user_by_cookie(cookie)
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = db.execute("SELECT file_name,total_chunks,current_chunk FROM uploads WHERE uploaded_by = ?", (user["username_hash"],)).fetchone()

    file_path = os.path.join(os.getenv("UPLOAD_ROOT"), user["username_hash"], result["file_name"])
    # No Upload found
    if result is None:
        return jsonify({"error": "No Upload found"}), 404
    # Chunk out of Range
    if chunk_index >= result["total_chunks"]:
        return jsonify({"error": "Chunk index out of range"}), 400
    # Tell Client to resend a Chunk if we have a Chunk Mismatch
    if chunk_index - 1 != result["current_chunk"] and result["current_chunk"] != 0:
        return jsonify({"error": "Chunk index mismatch. Resend Chunk","chunk" : result["current_chunk"]+1}), 400

    # Last Chunk that is uploaded length of Chunks - 1. => File has finished Uploading
    if chunk_index == result["total_chunks"] - 1:
        try:
            with open(file_path, "wb") as f:
                f.write(file.read())
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        db.execute("DELETE FROM uploads WHERE uploaded_by = ?", user["username_hash"])
        db.commit()
        return jsonify({"message": "File Uploaded Successfully"}), 200
    try:
        with open(file_path, "wb") as f:
            f.write(file.read())
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    db.execute("UPDATE uploads SET current_chunk = ? WHERE uploaded_by = ? ", (chunk_index, user["username_hash"]))
    db.commit()

    return jsonify({"message": "Chunk Uploaded Successfully"}), 202
