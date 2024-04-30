#!/usr/bin/env python3

from api.v1.views import app_views
from models import db, admin_datastore
from flask import request, make_response, jsonify
from flask_security import auth_required, login_user, logout_user, roles_required
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
            db.session.commit()
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
            if admin_user:
                admin_user.confirmed_at = datetime.now()
                admin_datastore.commit()
                return jsonify({'email': admin_user.email, 'verified': True}), 200
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
            return jsonify({'msg': True}), 200
        return jsonify({'error': 'either you suppiled a bad email or password or your email is still not confirmed yet'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'msg': False}), 400
