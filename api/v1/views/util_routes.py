
from api.v1.views import app_views
from models import instructor_datastore, student_datastore, InstAttendance \
                    , db, StuAttendance, app, Room, Booked
from flask import make_response, jsonify
from requests import get
from datetime import datetime
import redis

RedisConnection = redis.StrictRedis(
    host='localhost', port=6379, db=1, decode_responses=True
)


RedisConnection.set("finger_down", "False")



@app_views.route('/check/news', methods=['GET'], strict_slashes=False)
def check_newly_added():
    try:
        instructor = instructor_datastore.find_user(new=True)
        if not instructor:
            raise ValueError("no newly added instructor")
        return make_response(jsonify({'msg': True, 'id': instructor.id}), 200)
    except ValueError as e:
        try:
            student = student_datastore.find_user(new=True)
            if not student:
                raise ValueError(F"No newly added student & {str(e)}")
            return make_response(jsonify({'msg': True, 'id': student.id}), 200)
        except ValueError as e:
            return make_response(jsonify({'error': str(e), 'msg': False}))


@app_views.route('/register/<finger_id>/<id>', methods=['PUT', 'POST', 'GET'], strict_slashes=False)
def add_finger_id(finger_id, id):
    try:
        instructor = instructor_datastore.find_user(id=id)
        if not instructor:
            raise ValueError("no instructor")
        instructor.finger_id = finger_id
        instructor.new = False
        instructor_datastore.commit()
        return make_response(jsonify({'msg': True}), 200)
    except ValueError as e:
        try:
            student = student_datastore.find_user(id=id)
            if not student:
                raise ValueError(F"no student & {str(e)}")
            student.finger_id = finger_id
            student.new = False
            student_datastore.commit()
            return make_response(jsonify({'msg': True}), 200)
        except ValueError as e:
            return make_response(jsonify({'error': str(e)}))


@app_views.route('/verify/session/<finger_id>', methods=['GET', 'POST'], strict_slashes=False)
def verify_session(finger_id):
    try:
        uri = 'http://localhost:5000/api/v1'
        instructor = get(f"{uri}/instructor/fingerid/{finger_id}").json()
        if instructor['verified'] and instructor['biometric_verification']:
            sessions = InstAttendance.query.filter_by(instructor_id=instructor['id']).all()
            created_session = None
            for session in sessions:
                if not session.verified:
                    created_session = session
                    break
            if created_session:
                created_session.verified = True
                db.session.add(created_session)
                db.session.commit()
                return make_response(jsonify({'msg': True, 'type': 'instructor',
                                              'id': instructor["instructor_id"]}), 200)
            else:
                return make_response(jsonify({'error': "No session found", 'msg': False}), 200)
        else:
            raise ValueError("No instructor")
    except Exception as e:
        try:
            student = get(f"{uri}/student/fingerid/{finger_id}").json()
            if student['verified'] and student['biometric_verification']:
                classes = StuAttendance.query.filter_by(student_id=student['id']).all()
                open_class = None
                for clas in classes:
                    if not clas.end_time and not clas.arrived_time:
                        open_class = clas
                        break
                session = InstAttendance.query.filter(InstAttendance.id == open_class.session_id).first()
                if open_class and session.verified:
                    open_class.arrived_time = datetime.now()
                    db.session.add(open_class)
                    db.session.commit()
                    print(F"student id {open_class.student_id}")
                    print(F"id {open_class.id}")
                    print(open_class.arrived_time)
                    return make_response(jsonify({'msg': True,
                                                  'type': 'student',
                                                  'id': student["student_id"]}), 200)
                else:
                    return make_response(jsonify({'error': "No class found", 'msg': False}), 200)
            else:
                return make_response(jsonify({'error': 'either no student or instructor found or no email verification provided', 'msg': False}), 400)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 400)


@app_views.route("/verify/session/rfid/<rf_id>", methods=['GET', 'PUT'], strict_slashes=False)
def verify_session_using_rfid(rf_id):
    try:
        uri = 'http://localhost:5000/api/v1'
        instructor = get(f"{uri}/instructor/rfid/{rf_id}").json()
        if instructor['verified'] and instructor['RFID_verification']:
            sessions = InstAttendance.query.filter_by(instructor_id=instructor['id']).all()
            created_session = None
            for session in sessions:
                if not session.verified:
                    created_session = session
                    break
            if created_session:
                created_session.verified = True
                db.session.add(created_session)
                db.session.commit()
                return make_response(jsonify({'msg': True, 'type': 'instructor',
                                              'id': instructor["instructor_id"]}), 200)
            else:
                return make_response(jsonify({'error': "No session found", 'msg': False}), 200)
        else:
            raise ValueError("No instructor")
    except Exception as e:
        try:
            student = get(f"{uri}/student/rfid/{rf_id}").json()
            if student['verified'] and student['RFID_verification']:
                classes = StuAttendance.query.filter_by(student_id=student['id']).all()
                open_class = None
                for clas in classes:
                    if not clas.end_time and not clas.arrived_time:
                        open_class = clas
                        break
                session = InstAttendance.query.filter(InstAttendance.id == open_class.session_id).first()
                if open_class and session.verified:
                    open_class.arrived_time = datetime.now()
                    db.session.add(open_class)
                    db.session.commit()
                    return make_response(jsonify({'msg': True,
                                                  'type': 'student',
                                                  'id': student["student_id"]}), 200)
                else:
                    return make_response(jsonify({'error': "No class found", 'msg': False}), 200)
            else:
                return make_response(jsonify({'error': 'either no student or instructor found or no email verification provided', 'msg': False}), 400)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 400)



@app_views.route("/end/session/finger/<finger_id>", methods=['GET', 'PUT'], strict_slashes=False)
def delete_session_from_esp(finger_id):
    try:
        uri = 'http://localhost:5000/api/v1'
        instructor = get(f"{uri}/instructor/fingerid/{finger_id}").json()
        if instructor['verified'] and instructor['biometric_verification']:
            session = InstAttendance.query.filter(InstAttendance.instructor_id == instructor['id'])
            session = session.filter(InstAttendance.end_time == None).first()
            if session and eval(RedisConnection.get(session.id)):
                end_time = datetime.now()
                session.end_time = end_time
                rooms = Booked.query.filter(Booked.room_id == session.room_id)
                rooms = rooms.filter(Booked.over == False).all()
                for room in rooms:
                    room.over = True
                stu_attendees = session.student_attendance
                for stu_att in stu_attendees:
                    stu_att.end_time = end_time
                db.session.add_all(rooms)
                db.session.add_all(stu_attendees)
                db.session.add(session)
                db.session.commit()
                return make_response(jsonify({'msg': True, 'end_time': F"{end_time.day}/{end_time.month}/{end_time.year} {end_time.hour}:{end_time.minute}"}))
            else:
                return make_response(jsonify({'msg': False}))
        else:
            return make_response(jsonify({'error': "no instructor found", 'msg': False}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e), 'msg': False}), 400)


@app_views.route("/end/session/rfid/<rf_id>", methods=['GET', 'PUT'], strict_slashes=False)
def delete_session_from_esp_using_rfid(rf_id):
    try:
        uri = 'http://localhost:5000/api/v1'
        instructor = get(f"{uri}/instructor/rfid/{rf_id}").json()
        if instructor['verified'] and instructor['RFID_verification']:
            session = InstAttendance.query.filter(InstAttendance.instructor_id == instructor['id'])
            session = session.filter(InstAttendance.end_time == None).first()
            if session and eval(RedisConnection.get(session.id)):
                end_time = datetime.now()
                session.end_time = end_time
                rooms = Booked.query.filter(Booked.room_id == session.room_id)
                rooms = rooms.filter(Booked.over == False).all()
                for room in rooms:
                    room.over = True
                stu_attendees = session.student_attendance
                for stu_att in stu_attendees:
                    stu_att.end_time = end_time
                db.session.add_all(rooms)
                db.session.add_all(stu_attendees)
                db.session.add(session)
                db.session.commit()
                return make_response(jsonify({'msg': True, 'end_time': F"{end_time.day}/{end_time.month}/{end_time.year} {end_time.hour}:{end_time.minute}"}))
            else:
                return make_response(jsonify({'msg': False}))
        else:
            return make_response(jsonify({'error': "no instructor found", 'msg': False}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e), 'msg': False}), 400)


@app_views.route("/finger/down", methods=['GET', 'PUT'], strict_slashes=False)
def finger_is_down():
    RedisConnection.set("finger_down", "True")
    return make_response(jsonify({'msg': eval(RedisConnection.get("finger_down"))}))


@app_views.route("/finger/up", methods=['GET', 'PUT'], strict_slashes=False)
def finger_is_up():
    RedisConnection.set("finger_down", "False")
    return make_response(jsonify({'msg': eval(RedisConnection.get("finger_down"))}))


@app_views.route("/check/down", methods=['GET'], strict_slashes=False)
def check_if_finger_print_is_down():
    return make_response(jsonify({'msg': eval(RedisConnection.get("finger_down"))}))
