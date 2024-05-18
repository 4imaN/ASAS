
from models import db, Room, Booked
from flask import jsonify, request, make_response
from datetime import datetime, timedelta
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from flask_security import auth_required, login_user, logout_user, \
    roles_required, current_user, roles_accepted
from flask_security.utils import hash_password, verify_password
from flask_jwt_extended import get_current_user, jwt_required, unset_access_cookies, create_access_token
from utils.mailer import Mailer
from api.v1.views import app_views


@app_views.route('/room/auth/create', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_room():
    admin_user, user_type = get_current_user()
    if user_type != 'admin':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    # test
    request.form = request.get_json()
    block_no = request.form.get('block_no', None)
    room_no = request.form.get('room_no', None)
    already_room = Room.query.filter_by(block_no=block_no, room_no=room_no).first()
    if already_room:
        return make_response(jsonify({'error': f'Room already exists with id {already_room.id}'}), 400)
    try:
        room = Room(block_no=block_no, room_no=room_no)
        db.session.add(room)
        db.session.commit()
        return make_response(jsonify({'id': room.id,
                                      'block_no': room.block_no,
                                      'room_no': room.room_no,
                                      'created': True}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/room/update/<id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_room(id):
    admin_user, user_type = get_current_user()
    if user_type != 'admin':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    room = Room.query.filter_by(id=id).first()
    if not room:
        return make_response(jsonify({'error': F'room with id {room.id} doesnt exist'}), 400)
    try:
        # test
        request.form = request.get_json()
        block_no = request.form.get('block_no', None)
        room_no = request.form.get('room_no', None)
        if block_no:
            room.block_no = block_no
        if room_no:
            room.room_no = room_no
        db.session.add(room)
        db.session.commit()
        return make_response(jsonify({'id': room.id,
                                      'block_no': room.block_no,
                                      'room_no': room.room_no,
                                      'updated': True}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/room/get', methods=['GET'], strict_slashes=False)
def get_rooms():
    # test
    # request.form = request.get_json()
    id = request.args.get('id', None)
    block_no = request.args.get('block_no', None)
    room_no = request.args.get('room_no', None)
    try:
        room = Room.query
        if id:
            room = room.filter(Room.id == id)
        if block_no:
            room = room.filter(Room.block_no == block_no)
        if room_no:
            room = room.filter(Room.room_no == room_no)
        if not room:
            return make_response(jsonify({'error': 'no room found'}), 404)
        room = room.all()
        booked_id = [i.id for i in Booked.query.all() if i.over == False]
        response = []
        for r in room:
            response.append({
                'id': r.id,
                'room': r.block_no + ' ' + r.room_no,
                'is_booked': True if r.id in booked_id else False
            })
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
