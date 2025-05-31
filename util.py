from flask import Blueprint, render_template

from db import get_db

util_bp = Blueprint('util', __name__, url_prefix='/util')


@util_bp.route('/gen_keys')
def genkeys():
    return render_template('utility/keygen.html')



def cleanup():
    db = get_db()
    db.execute("DELETE FROM cookies WHERE created < datetime('now','-2 hours')")
    db.execute("DELETE FROM data_packet WHERE id IN (SELECT dp.id FROM data_packet dp JOIN users user on user.id = dp.sender_user_id WHERE dp.uploaded_at < datetime('now','-' || user.retention_seconds || ' seconds'))")
