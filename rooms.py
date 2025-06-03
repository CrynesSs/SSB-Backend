from flask import request, render_template, Blueprint

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

# Shows the rooms this user is a member of
@rooms_bp.route('/',methods=['POST'])
def rooms():
    data = request.get_json()
    return "TODO"


