
from models import db, instructor_datastore, admin_datastore, student_datastore
from flask import jsonify, request, make_response
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from flask_security import auth_required, login_user, logout_user, \
    roles_required, current_user, roles_accepted
from flask_security.utils import hash_password, verify_password
from flask_jwt_extended import get_current_user, jwt_required, unset_access_cookies, create_access_token
from utils.mailer import Mailer
from api.v1.views import app_views



@app_views.route('/instructor/auth/register', methods=['POST'], strict_slashes=False)
@jwt_required()
def instructor_reg():
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        if request.method == 'POST':
            # below line is for testing purpose
            request.form = request.get_json()
            first_name = request.form.get('first_name', None)
            last_name = request.form.get('last_name', None)
            middle_name = request.form.get('middle_name', None)
            gender = request.form.get('gender', None)
            department = request.form.get('department', None)
            email = request.form.get('email', None)
            password = request.form.get('password')
            teacher_id = request.form.get('teacher_id', None)
            qualification = request.form.get('qualification', None)
            password = hash_password(password)
            if instructor_datastore.get_user(email) or admin_datastore.get_user(email) or student_datastore.get_user(email):
                return make_response(jsonify({'error': 'Email already exists'}), 400)
            try:
                instructor_role = instructor_datastore.find_or_create_role('instructor')
                instructor = instructor_datastore.create_user(email=email, first_name=first_name,
                                                            middle_name=middle_name, last_name=last_name,
                                                            gender=gender, department=department,
                                                            password=password, teacher_id=teacher_id,
                                                            qualification=qualification)
                instructor_datastore.add_role_to_user(instructor, instructor_role)
                instructor_datastore.commit()
                email_verifier = Mailer(instructor.email)
                token = email_verifier.set_token()
                email_verifier.set_body()
                email_verifier.send_mail()
                return make_response(jsonify({'email': instructor.email, 'instructor': True, 'id': instructor.id}), 201)
            except (SQLAlchemyError, OperationalError, IntegrityError) as e:
                return make_response(jsonify({'error': str(e), 'instructor': False}), 400)
        return make_response(jsonify({"error": 'URL doesnt exist'}), 404)


@app_views.route('/instructor/auth/login', methods=['POST'], strict_slashes=False)
def instructor_login():
    try:
        # below line is for testing purpose
        request.form = request.get_json()
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        instructor = instructor_datastore.find_user(email=email)
        if instructor and instructor.confirmed_at and verify_password(password, instructor.password):
            login_user(instructor)
            instructor_datastore.commit()
            db.session.add(instructor)
            db.session.commit()
            data = {'type': 'instructor'}
            access_token = create_access_token(identity=instructor.id, additional_claims=data)
            res = make_response(jsonify({'msg': True}), 200)
            res.set_cookie('access_token_cookie', access_token)
            return res
        return jsonify({'error': 'either you supplied a bad email or password or your email is still not confirmed yet'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'msg': False}), 400


@app_views.route('/instructor/update/<id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def instructor_update(id):
    try:
        user, user_type = get_current_user()
        if user.confirmed_at:
            instructor = instructor_datastore.find_user(id=id)
            if not instructor:
                return make_response(jsonify({'error': 'intructor not found'}), 400)
            if user_type == 'admin':
                updatables = ['teacher_id',
                        'password', 'department', 'finger_id',
                        'rf_id', 'qualification']
                data = request.get_json()
                for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
                for k, v in data.items():
                    if k == 'password':
                        v = hash_password(v)
                    setattr(instructor, k, v)
                instructor_datastore.commit()
                res_dict = {k: getattr(instructor, k) for k in updatables if k in data.keys() and k != 'password'}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            elif user_type == 'instructor':
                updatables = ['password']
                data = request.get_json()
                for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
                for k, v in data.items():
                    if k == 'password':
                        v = hash_password(v)
                    setattr(instructor, k, v)
                instructor_datastore.commit()
                res_dict = {k: getattr(instructor, k) for k in updatables if k in data.keys() and k != 'password'}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            else:
                return make_response(jsonify({"error": 'URL doesnt exist'}), 404)
        return jsonify({'error': 'user needs to confirm first', 'updated': False}), 400
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/instructor/delete/<id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def instructor_del(id):
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        instructor = instructor_datastore.find_user(id=id)
        if admin_user.confirmed_at:
            instructor_datastore.deactivate_user(instructor)
            instructor_datastore.delete(instructor)
            instructor_datastore.commit()
            return jsonify({'msg': True}), 200
        return jsonify({'error': 'user needs to confirm first', 'deleted': False}), 400
    return make_response(jsonify({"error": 'URL doesnt exist'}), 404)


@app_views.route('/instructor/<rf_id>', methods=['GET'], strict_slashes=False)
def instructor_check_rf_id(rf_id):
    instructor = instructor_datastore.find_user(rf_id=rf_id)
    if not instructor:
        return jsonify({'verified': False}), 400
    elif instructor and not instructor.confirmed_at:
        return jsonify({'verified': False, 'id': instructor.id,
                        'first_name': instructor.first_name,
                        'RFID_verification': True}), 200
    elif instructor and instructor.confirmed_at:
        return jsonify({'verified': True, 'id': instructor.id,
                        'first_name': instructor.first_name,
                        'RFID_verification': True}), 200


@app_views.route('/instructor/<finger_id>', methods=['GET'], strict_slashes=False)
def instructor_check_finger_id(finger_id):
    instructor = instructor_datastore.find_user(finger_id=finger_id)
    if not instructor:
        return jsonify({'verified': False}), 400
    elif instructor and not instructor.confirmed_at:
        return jsonify({'verified': False, 'id': instructor.id,
                        'first_name': instructor.first_name,
                        'biometric_verification': True}), 200
    elif instructor and instructor.confirmed_at:
        return jsonify({'verified': True, 'id': instructor.id,
                        'first_name': instructor.first_name,
                        'biometric_verification': True}), 200

@app_views.route('/instructor/auth/logout', methods=['GET', 'POST'], strict_slashes=False)
def instructor_logout():
    instructor, user_type = get_current_user()
    if user_type == 'instructor':
        if instructor and instructor.confirmed_at:
            logout_user()
            res = make_response(jsonify({'msg': True}), 200)
            unset_access_cookies(res)
            return res
        return jsonify({'error': 'either user doesnt exist or account not verified yet'}), 400
    return make_response(jsonify({"error": 'URL doesnt exist'}), 404)


@app_views.route('/instructor/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def instructor_me():
    instructor, user_type = get_current_user()
    if user_type == 'instructor':
        return make_response(jsonify({'first_name': instructor.first_name,
                                      'middle_name': instructor.middle_name,
                                      'last_name': instructor.last_name,
                                      'gender': instructor.gender,
                                      'teacher_id': instructor.teacher_id,
                                      'email': instructor.email,
                                      'department': instructor.department,
                                      'qualification': instructor.qualification,
                                      }), 200)
    return make_response(jsonify({'error': 'URL doesnt exist'}), 404)


# @app_views.route('/instructor/assign-student/')
# to be done
# assigning students to a course and instructor
# create class session
# automatic student attendance tracking for session
