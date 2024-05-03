
from models import app, instructor_datastore, admin_datastore, student_datastore
from flask import jsonify, abort, request, make_response
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from flask_security import auth_required, login_user, logout_user, \
    roles_required, current_user, roles_accepted, login_required, Security
from flask_security.utils import hash_password, verify_password
from flask_jwt_extended import jwt_required, get_current_user ,unset_access_cookies, create_access_token
from utils.mailer import Mailer
from api.v1.views import app_views


@app_views.route('/student/auth/register', methods=['POST'], strict_slashes=False)
@jwt_required(9)
def student_reg():
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
    return make_response(jsonify({'error': 'url doesnt exist'}), 400)


@app_views.route('/student/auth/login', methods=['POST'], strict_slashes=False)
def student_login():
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
    try:
        user, user_type = get_current_user()
        if user.confirmed_at:
            student = student_datastore.find_user(id=id)
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
                    setattr(student, k, v)
                student_datastore.commit()
                res_dict = {k: getattr(student, k) for k in updatables if k in data.keys()}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            elif user_type == 'student':
                updatables = ['password']
                data = request.get_json()
                for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
                for k, v in data.items():
                    setattr(student, k, v)
                student_datastore.commit()
                res_dict = {k: getattr(student, k) for k in updatables if k in data.keys()}
                res_dict.update({'updated': True})
                return jsonify(res_dict), 200
            else:
                return make_response(jsonify({"error": 'url doesnt exist'}), 400)
        return jsonify({'error': 'user needs to confirm first', 'updated': False}), 400
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)