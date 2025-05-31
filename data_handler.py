from flask import request, jsonify

from app import app
from db import get_db


@app.route("/upload-data", methods=["POST"])
def upload_data():
    data = request.get_json()
    recipient_hash = data["recipient_username_hash"]
    blob = bytes.fromhex(data["data"])  # or base64 decode

    db = get_db()
    user = db.execute("SELECT id, max_storage_bytes FROM users WHERE username_hash = ?", (recipient_hash,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Calculate total used storage
    usage = db.execute("SELECT COALESCE(SUM(LENGTH(data)), 0) as total FROM user_data WHERE recipient_user_id = ?", (user["id"],)).fetchone()

    if usage["total"] + len(blob) > user["max_storage_bytes"]:
        return jsonify({"error": "Storage limit exceeded"}), 403

    db.execute(
        "INSERT INTO user_data (recipient_user_id, data) VALUES (?, ?)",
        (user["id"], blob)
    )
    db.commit()

    return jsonify({"status": "data stored"})
