
from models import app, instructor_datastore, admin_datastore, \
    student_datastore, InstAttendance, StuAttendance, db
from datetime import datetime
from flask import jsonify, abort, request, make_response
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from flask_security import auth_required, login_user, logout_user, \
    roles_required, current_user, roles_accepted, login_required, Security
from flask_security.utils import hash_password, verify_password
from flask_jwt_extended import jwt_required, get_current_user ,unset_access_cookies, create_access_token
from utils.mailer import Mailer
from api.v1.views import app_views
from requests import get


@app_views.route('/student/auth/register', methods=['POST'], strict_slashes=False)
@jwt_required()
def student_reg():
    """
    registers a new student in the system if the current user is an admin and
    handles error responses accordingly.
    """
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        if request.method == 'POST' or admin_user.confirmed_at:
            # below line is for testing purpose
            request.form = request.get_json()
            first_name = request.form.get('first_name', None)
            last_name = request.form.get('last_name', None)
            middle_name = request.form.get('middle_name', None)
            gender = request.form.get('gender', None)
            department = request.form.get('department', None)
            email = request.form.get('email', None)
            password = request.form.get('password')
            student_id = request.form.get('student_id', None)
            batch_section = request.form.get('batch_section', None)
            password = hash_password(password)
            if instructor_datastore.get_user(email) or admin_datastore.get_user(email) or student_datastore.get_user(email):
                return make_response(jsonify({'error': 'Email already exists'}), 400)
            try:
                student_role = student_datastore.find_or_create_role('student')
                student = student_datastore.create_user(email=email, first_name=first_name,
                                                            middle_name=middle_name, last_name=last_name,
                                                            gender=gender, department=department,
                                                            password=password, student_id=student_id,
                                                            batch_section=batch_section)
                student_datastore.add_role_to_user(student, student_role)
                student_datastore.commit()
                email_verifier = Mailer(student.email)
                token = email_verifier.set_token()
                email_verifier.set_body()
                email_verifier.send_mail()
                return make_response(jsonify({'email': student.email, 'student': True, 'id': student.id}), 201)
            except (SQLAlchemyError, OperationalError, IntegrityError) as e:
                return make_response(jsonify({'error': str(e), 'student': False}), 400)
        return make_response(jsonify({'error': 'email not verified'}), 400)
    return make_response(jsonify({'error': 'url doesnt exist'}), 400)


@app_views.route('/student/auth/login', methods=['POST'], strict_slashes=False)
def student_login():
    """
    function attempts to authenticate a student user based on the provided email and
    password, setting a cookie with an access token upon successful login.
    """
    try:
        # below line is for testing purpose
        request.form = request.get_json()
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        student = student_datastore.find_user(email=email)
        if student and student.confirmed_at and verify_password(password, student.password):
            login_user(student)
            admin_datastore.commit()
            data = {'type': 'student'}
            access_token = create_access_token(identity=student.id, additional_claims=data)
            res = make_response(jsonify({'msg': True}), 200)
            res.set_cookie('access_token_cookie', access_token)
            return res
        return jsonify({'error': 'either you supplied a bad email or password or your email is still not confirmed yet'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'msg': False}), 400


@app_views.route('/student/update/<id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def student_update(id):
    """
    updates student information based on user type and input data,
    handling different cases and error scenarios.
    """
    try:
        user, user_type = get_current_user()
        if user.confirmed_at:
            student = student_datastore.find_user(id=id)
            if not student:
                return make_response(jsonify({'error': 'student not found'}), 400)
            if user_type == 'admin':
                updatables = ['student_id',
                        'password', 'department', 'finger_id',
                        'rf_id', 'batch_section',
                        'registered', 'add']
                data = request.get_json()
                for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
                for k, v in data.items():
                    if k == 'password':
                        v = hash_password(v)
                    setattr(student, k, v)
                student_datastore.commit()
                res_dict = {k: getattr(student, k) for k in updatables if k in data.keys() and k != 'password'}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            elif user_type == 'student':
                updatables = ['password']
                data = request.get_json()
                for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
                for k, v in data.items():
                    if k == 'password':
                        v = hash_password(v)
                    setattr(student, k, v)
                student_datastore.commit()
                res_dict = {k: getattr(student, k) for k in updatables if k in data.keys() and k != 'password'}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            else:
                return make_response(jsonify({"error": 'URL doesnt exist'}), 404)
        return jsonify({'error': 'user needs to confirm first', 'updated': False}), 400
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)



@app_views.route('/student/delete/<id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def student_del(id):
    """
    deletes a student user from the datastore if the current user is an admin
    and the admin user has been confirmed.
    """
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        student = student_datastore.find_user(id=id)
        if admin_user.confirmed_at:
            student_datastore.deactivate_user(student)
            student_datastore.delete(student)
            student_datastore.commit()
            return jsonify({'msg': True}), 200
        return jsonify({'error': 'user needs to confirm first', 'deleted': False}), 400
    return make_response(jsonify({"error": 'URL doesnt exist'}), 404)



@app_views.route('/student/rfid/<rf_id>', methods=['GET'], strict_slashes=False)
def student_check_rf_id(rf_id):
    student = student_datastore.find_user(rf_id=rf_id)
    if not student:
        return jsonify({'verified': False}), 400
    elif student and not student.confirmed_at:
        return jsonify({'verified': False, 'id': student.id,
                        'first_name': student.first_name,
                        'RFID_verification': True}), 200
    elif student and student.confirmed_at:
        return jsonify({'verified': True, 'id': student.id,
                        'first_name': student.first_name,
                        'RFID_verification': True}), 200


@app_views.route('/student/fingerid/<finger_id>', methods=['GET'], strict_slashes=False)
def student_check_finger_id(finger_id):
    student = student_datastore.find_user(finger_id=finger_id)
    if not student:
        return jsonify({'verified': False}), 400
    elif student and not student.confirmed_at:
        return jsonify({'verified': False, 'id': student.id,
                        'first_name': student.first_name,
                        'biometric_verification': True}), 200
    elif student and student.confirmed_at:
        return jsonify({'verified': True, 'id': student.id,
                        'first_name': student.first_name,
                        'biometric_verification': True}), 200


@app_views.route('/student/auth/logout', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
def student_logout():
    student, user_type = get_current_user()
    if user_type == 'student':
        if student and student.confirmed_at:
            logout_user()
            res = make_response(jsonify({'msg': True}), 200)
            unset_access_cookies(res)
            return res
        return jsonify({'error': 'either user doesnt exist or account not verified yet'}), 400
    return make_response(jsonify({"error": 'URL doesnt exist'}), 404)


@app_views.route('/student/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def student_me():
    student, user_type = get_current_user()
    if user_type == 'student':
        return make_response(jsonify({'first_name': student.first_name,
                                      'middle_name': student.middle_name,
                                      'last_name': student.last_name,
                                      'gender': student.gender,
                                      'registered': student.registered,
                                      'student_id': student.student_id,
                                      'email': student.email,
                                      'department': student.department,
                                      'batch': student.batch_section.split(" ")[0],
                                      'section': student.batch_section.split(" ")[1],
                                      'id': student.id
                                      }), 200)
    return make_response(jsonify({'error': 'URL doesnt exist'}), 404)


@app_views.route('/student/verify-session/<session_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def verify_session_student(session_id):
    student, user_type = get_current_user()
    if user_type != 'student':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    session = InstAttendance.query.filter_by(id=session_id).first()
    if not session:
        return make_response(jsonify({'error': 'Session not found'}), 404)
    student_attendance_obj_found = False
    student_attendance = None
    for student_att in session.student_attendance:
        if student_att.student_id == student.id:
            student_attendance_obj_found = True
            student_attendance = student_att
    if not student_attendance_obj_found:
        return make_response(jsonify({'error': 'no student attendance created'}), 404)
    # test
    request.form = request.get_json()
    finger_id = request.form.get('finger_id', None)
    rf_id = request.form.get('rf_id', None)
    verified = False
    data = None
    uri = 'http://localhost:5000/api'
    try:
        if finger_id:
            data = get(f'{uri}/student/fingerid/{finger_id}').json
            if data['verified']:
                if data['student_id'] == student_attendance.student_id and not student_attendance.arrived_time:
                    student_attendance.arrived_time = datetime.now()
                    db.session.add(student_attendance)
                    db.session.commit()

                    verified = True
                    return make_response(jsonify({'verified': verified}), 200)
        if rf_id:
            data = get(f'{uri}/student/rfid/{rf_id}').json
            if data['verified']:
                if data['student_id'] == student_attendance.student_id and student_attendance.arrived_time:
                    student_attendance.arrived_time = datetime.now()
                    db.session.add(student_attendance)
                    db.session.commit()

                    verified = True        
                    return make_response(jsonify({'verified': verified}), 200)
        return make_response(jsonify({'verified': verified}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/student/attendance/<course_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def student_attendance_list(course_id):
    instructor, user_type = get_current_user()
    if user_type != 'instructor':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    try:
        attendance_list = StuAttendance.query.filter(StuAttendance.course_id == course_id)
        attendance_list = attendance_list.filter(StuAttendance.instructor_id == instructor.id)
        temp_attendance_list = attendance_list
        attendance_list.all()
        response = []
        for student_attendance in attendance_list:
            student_id = student_attendance.student_id
            student_list = temp_attendance_list
            student_list.filter(StuAttendance.student_id == student_id)
            student_list.filter(StuAttendance.end_time != None)
            student_list = student_list.all()
            available = 0
            for student in student_list:
                if student.arrived_time:
                    available += 1
            student = student_datastore.find_user(id=student_id)
            response.append({
                'total_class': len(student_list),
                'attended': available,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'middle_name': student.middle_name,
                'email': student.email,
                'student_id': student.student_id,
                'id': student_id
            })
        return make_response(jsonify(response), 200)
    except Exception as e :
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/student/my-attendance/<course_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_my_attendance(course_id):
    student, user_type = get_current_user()
    if user_type != 'student':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    course_attendance = StuAttendance.query.filter(StuAttendance.course_id == course_id)
    course_attendance = course_attendance.filter(StuAttendance.student_id == student.id)
    course_attendance = course_attendance.all()
    response = []
    for cour_att in course_attendance:
        # cour_att.start_time = datetime.strptime(cour_att.start_time, "%Y-%m-%d %H:%M:%S")
        # cour_att.end_time = datetime.strptime(cour_att.end_time, "%Y-%m-%d %H:%M:%S")
        # cour_att.arrived_time = datetime.strptime(cour_att.arrived_time, "%Y-%m-%d %H:%M:%S")
        response.append({
            'class_date': f"{cour_att.start_time.day}/{cour_att.start_time.month}/{cour_att.start_time.year}",
            'at': f"{cour_att.start_time.hour}:{cour_att.start_time.minute}",
            'arrived_at': f"{cour_att.arrived_time.hour}:{cour_att.arrived_time.minute}"
        })
    return make_response(jsonify(response), 200)
