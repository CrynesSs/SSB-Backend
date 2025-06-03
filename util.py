import base64
import hashlib
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hashes import SHA256, HashAlgorithm
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Blueprint, render_template

from db import get_db

util_bp = Blueprint('util', __name__, url_prefix='/util')


def cleanup():
    db = get_db()
    db.execute("DELETE FROM cookies WHERE created < datetime('now','-2 hours')")
    db.execute("DELETE FROM data_packet WHERE id IN (SELECT dp.id FROM data_packet dp JOIN users user on user.id = dp.sender_user_id WHERE dp.uploaded_at < datetime('now','-' || user.retention_seconds || ' seconds'))")


def generate_salt(length=16) -> str:
    return base64.b64encode(os.urandom(length)).decode()

def hash_with_salt(value: str, salt: str) -> str:
    """Securely hash a value with a given salt using PBKDF2-HMAC-SHA256."""
    salt_bytes = base64.b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=100_000,
    )
    hash_bytes = kdf.derive(value.encode())
    return base64.b64encode(hash_bytes).decode()