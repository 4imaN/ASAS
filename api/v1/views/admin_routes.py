

from api.v1.views import app_views
from models import app, admin_datastore, instructor_datastore, student_datastore
from flask import request, make_response, jsonify
from flask_security import (
                            auth_required,
                            login_user,
                            logout_user,
                            roles_required
                            )
from flask_jwt_extended import jwt_required, get_current_user
from flask_jwt_extended import create_access_token, unset_access_cookies
from flask_security.utils import hash_password, verify_password
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError, NoResultFound
from utils.mailer import Mailer
from datetime import datetime



@app_views.route('/admin/auth/register', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
def admin_reg():
    user, user_type = get_current_user()
    if request.method == 'POST' and user_type == 'admin':
        # below line is for testing purpose
        request.form = request.get_json()
        first_name = request.form.get('first_name', None)
        last_name = request.form.get('last_name', None)
        middle_name = request.form.get('middle_name', None)
        gender = request.form.get('gender', None)
        department = request.form.get('department', None)
        email = request.form.get('email', None)
        password = request.form.get('password')
        if admin_datastore.get_user(email) or instructor_datastore.get_user(email) or student_datastore.get_user(email):
            return make_response(jsonify({'error': 'Email already exists'}), 400)
        try:
            password = hash_password(password)
            admin_role = admin_datastore.find_or_create_role('admin')
            admin_user = admin_datastore.create_user(email=email, password=password,
                                                 first_name=first_name, middle_name=middle_name,
                                                 last_name=last_name, gender=gender,
                                                 department=department)
            admin_datastore.add_role_to_user(admin_user, admin_role)
            # db.session.commit()
            admin_datastore.commit()
            email_verifier = Mailer(admin_user.email)
            token = email_verifier.set_token()
            email_verifier.set_body()
            email_verifier.send_mail()
            res = make_response(jsonify({'email': admin_user.email, 'admin': True, 'id': admin_user.id}), 201)
            return res
        except (SQLAlchemyError, OperationalError, IntegrityError) as e:
            return make_response(jsonify({'error': str(e), 'admin': False}), 400)
    return make_response(jsonify({"error": 'url doesnt exist'}), 400)


@app_views.route('/auth/verify-email/<token>', methods=['GET', 'POST'], strict_slashes=False)
def verify_email(token):
    try:
        email = Mailer.get_email(token)
        if not email:
            raise NoResultFound('Email cant be recognized')
        try:
            admin_user = admin_datastore.find_user(email=email)
            if not admin_user:
                raise NoResultFound('User is not admin')
            if not admin_user.confirmed_at:
                admin_user.confirmed_at = datetime.now()
                admin_datastore.commit()
                return make_response(jsonify({'email': admin_user.email, 'verified': True,
                                              'type': admin_user.__class__.__name__}), 200)
            else:
                return make_response(jsonify({'error': 'already verified'}), 400)
        except Exception:
            # try block must be implemented for instructors
            try:
                instructor = instructor_datastore.find_user(email=email)
                if not instructor:
                    raise NoResultFound('User not instructor')
                if not instructor.confirmed_at:
                    instructor.confirmed_at = datetime.now()
                    instructor_datastore.commit()
                    return make_response(jsonify({'email': instructor.email, 'verified': True,
                                                  'type': instructor.__class__.__name__}), 200)
                else:
                    return make_response(jsonify({'error': 'already verified'}), 400)
            except Exception:
                # try block must be implemented for students
                try:
                    student = student_datastore.find_user(email=email)
                    if not student:
                        raise NoResultFound('User not student')
                    if not student.confirmed_at:
                        student.confirmed_at = datetime.now()
                        student_datastore.commit()
                        return make_response(jsonify({'email': student.email, 'verified': True,
                                                    'type': student.__class__.__name__}), 200)
                    else:
                        return make_response(jsonify({'error': 'already verified'}), 400)
                except Exception:
                    return make_response(jsonify({}), 400)

    except Exception as e:
        return jsonify({'error': str(e), 'verified': False}), 400


@app_views.route('/admin/auth/login', methods=['POST'], strict_slashes=False)
def admin_login():
    try:
        # below line is for testing purpose
        request.form = request.get_json()
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        admin_user = admin_datastore.find_user(email=email)
        if admin_user and admin_user.confirmed_at and verify_password(password, admin_user.password):
            login_user(admin_user)
            admin_datastore.commit()
            data = {'type': 'admin'}
            access_token = create_access_token(identity=admin_user.id, additional_claims=data)
            res = make_response(jsonify({'msg': True}), 200)
            res.set_cookie('access_token_cookie', access_token)
            return res
        return jsonify({'error': 'either you supplied a bad email or password or your email is still not confirmed yet'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'msg': False}), 400


@app_views.route('/admin/update', methods=['PUT'], strict_slashes=False)
@jwt_required()
def admin_update():
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        if admin_user.confirmed_at:
            updatables = ['department', 'finger_id', 'rf_id']
            data = request.get_json()
            for k in data.keys():
                if k not in updatables:
                    return jsonify({'error': f'key {k} not updatable or not available'}), 400
            for k, v in data.items():
                if k == 'password':
                        v = hash_password(v)
                setattr(admin_user, k, v)
            admin_datastore.commit()
            res_dict = {k: getattr(admin_user, k) for k in updatables if k in data.keys() and k != 'password'}
            res_dict.update({'updated': True})
            return jsonify(res_dict), 200
        return jsonify({'error': 'user needs to confirm first', 'updated': False}), 400
    return make_response(jsonify({"error": 'url doesnt exist'}), 400)


@app_views.route('/admin/delete', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_del():
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        if admin_user.confirmed_at:
            admin_datastore.deactivate_user(admin_user)
            admin_datastore.delete(admin_user)
            admin_datastore.commit()
            return jsonify({'msg': True}), 200
        return jsonify({'error': 'user needs to confirm first', 'deleted': False}), 400
    return make_response(jsonify({"error": 'url doesnt exist'}), 400)


@app_views.route('/admin/fingerid/<finger_id>', methods=['GET'], strict_slashes=False)
def admin_check_finger_id(finger_id):
    admin_user = admin_datastore.find_user(finger_id=finger_id)
    if not admin_user:
        return jsonify({'verified': False}), 400
    elif admin_user and not admin_user.confirmed_at:
        return jsonify({'verified': False, 'id': admin_user.id,
                        'first_name': admin_user.first_name,
                        'biometric_verification': True}), 200
    elif admin_user and admin_user.confirmed_at:
        return jsonify({'verified': True, 'id': admin_user.id,
                        'first_name': admin_user.first_name,
                        'biometric_verification': True}), 200


@app_views.route('/admin/rfid/<rf_id>', methods=['GET'], strict_slashes=False)
def admin_check_rf_id(rf_id):
    admin_user = admin_datastore.find_user(rf_id=rf_id)
    if not admin_user:
        return jsonify({'verified': False}), 400
    elif admin_user and not admin_user.confirmed_at:
        return jsonify({'verified': False, 'id': admin_user.id,
                        'first_name': admin_user.first_name,
                        'RFID_verification': True}), 200
    elif admin_user and admin_user.confirmed_at:
        return jsonify({'verified': True, 'id': admin_user.id,
                        'first_name': admin_user.first_name,
                        'RFID_verification': True}), 200


@app_views.route('/admin/auth/logout', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
def admin_logout():
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        if admin_user and admin_user.confirmed_at:
            logout_user()
            res = make_response(jsonify({'msg': True}), 200)
            unset_access_cookies(res)
            return res
        return jsonify({'error': 'either user doesnt exist or account not verified yet'}), 400
    return make_response(jsonify({"error": 'url doesnt exist'}), 400)


@app_views.route('/admin/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_me():
    admin, user_type = get_current_user()
    if user_type == 'admin':
        return make_response(jsonify({'first_name': admin.first_name,
                                      'middle_name': admin.middle_name,
                                      'last_name': admin.last_name,
                                      'gender': admin.gender,
                                      'email': admin.email,
                                      'department': admin.department,
                                      'id': admin.id
                                      }), 200)
    return make_response(jsonify({'error': 'url doesnt exist'}), 400)