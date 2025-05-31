from flask import request, render_template, Blueprint

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

# Shows the rooms this user is a member of
@rooms_bp.route('/')
def rooms():
    #username = request.form['username']

    rooms_data = [
        {"id": 1, "name": "Room A"},
        {"id": 2, "name": "Room B"},
        {"id": 3, "name": "Room C"},
    ]
    return render_template('rooms/room.html', title='Rooms', rooms=rooms_data)

