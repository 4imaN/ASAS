#!/usr/bin/env python3

from api.v1.views import app_views
from models import admin_datastore
from flask import request, make_response, jsonify
from flask_security import auth_required, login_user, logout_user, roles_required, current_user
from flask_security.utils import hash_password, verify_password
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from utils.mailer import Mailer
from datetime import datetime


@app_views.route('/admin/auth/register', methods=['GET', 'POST'], strict_slashes=False)
# @roles_required('admin')
# @auth_required('token', 'session')
def admin_reg():
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
        if admin_datastore.get_user(email):
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
            return make_response(jsonify({'email': admin_user.email, 'admin': True, 'id': admin_user.id}), 201)
        except (SQLAlchemyError, OperationalError, IntegrityError) as e:
            return make_response(jsonify({'error': str(e), 'admin': False}), 400)


@app_views.route('/auth/verify-email/<token>', methods=['GET', 'POST'], strict_slashes=False)
def verify_email(token):
    try:
        email = Mailer.get_email(token)
        try:
            admin_user = admin_datastore.find_user(email=email)
            if not admin_user:
                return jsonify({'error': 'user doesnt exist'}), 400
            if not admin_user.confirmed_at:
                admin_user.confirmed_at = datetime.now()
                admin_datastore.commit()
                return jsonify({'email': admin_user.email, 'verified': True}), 200
            else:
                return jsonify({'error': 'already verified'}), 400
        except Exception:
            # try block must be implemented for instructors and students
            return jsonify(), 400
    except Exception as e:
        return jsonify({'error': str(e), 'verified': False}), 400


@app_views.route('/admin/auth/login', methods=['POST'], strict_slashes=False)
def admin_login():
    try:
        request.form = request.get_json()
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        admin_user = admin_datastore.find_user(email=email)
        if admin_user and admin_user.confirmed_at and verify_password(password, admin_user.password):
            login_user(admin_user)
            admin_datastore.commit()
            return jsonify({'msg': True}), 200
        return jsonify({'error': 'either you suppiled a bad email or password or your email is still not confirmed yet'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'msg': False}), 400


@app_views.route('/admin/update', methods=['PUT'], strict_slashes=False)
@roles_required('admin')
@auth_required('session', 'token')
def admin_update():
    admin_user = current_user
    if admin_user.confirmed_at:
        updatables = ['department', 'finger_id', 'rf_id']
        data = request.get_json()
        for k in data.keys():
            if k not in updatables:
                return jsonify({'error': f'key {k} not updatable or not available'}), 400
        for k, v in data.items():
            setattr(admin_user, k, v)
        admin_datastore.commit()
        res_dict = {k: data[k] for k in updatables if k in data.keys()}
        res_dict.update({'updated': True})
        return jsonify(res_dict), 200
    return jsonify({'error': 'user needs to confirm first', 'updated': False}), 400


@app_views.route('/admin/delete', methods=['DELETE'], strict_slashes=False)
@roles_required('admin')
@auth_required('session', 'token')
def admin_del():
    admin_user = current_user
    if admin_user.confirmed_at:
        admin_datastore.deactivate_user(admin_user)
        admin_datastore.delete(admin_user)
        admin_user.active = True
        admin_user.is_active = True
        admin_datastore.commit()
        return jsonify({'msg': True}), 200
    return jsonify({'error': 'user needs to confirm first', 'deleted': False}), 400


@app_views.route('/admin/<finger_id>', methods=['GET'], strict_slashes=False)
def check_finger_id(finger_id):
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


@app_views.route('/admin/<rf_id>', methods=['GET'], strict_slashes=False)
def check_rf_id(rf_id):
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
@roles_required('admin')
@auth_required('session', 'token')
def admin_logout():
    admin_user = current_user
    if admin_user and admin_user.confirmed_at:
        logout_user()
        return jsonify({'msg': True}), 200
    return jsonify({'error': 'either user doesnt exist or account not verified yet'}), 400
