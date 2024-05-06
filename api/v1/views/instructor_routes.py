
from models import db, instructor_datastore, \
    admin_datastore, student_datastore, AssignedStudent, Course, \
    Instructor, Student
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
    """
    registers a new instructor in the system, handling form data, hashing
    passwords, checking for existing emails, creating user roles,
    sending verification emails, and handling exceptions.
    """
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
    """
    handles instructor login by verifying email, password, and
    confirmation status.
    """
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
    """
    updates instructor information based on user type and provided
    data, handling different scenarios and error cases.
    """
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
    """
    This Python function deactivates and deletes an instructor user 
    if the current user is an admin and has confirmed their account.
    """
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


@app_views.route('/instructor/rfid/<rf_id>', methods=['GET'], strict_slashes=False)
def instructor_check_rf_id(rf_id):
    """
    checks if an instructor with a given RFID exists and if their
    RFID has been confirmed.
    """
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


@app_views.route('/instructor/fingerid/<finger_id>', methods=['GET'], strict_slashes=False)
def instructor_check_finger_id(finger_id):
    """
    checks if an instructor with a given finger ID exists in the datastore and returns
    their verification status along with other details if applicable.
    """
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
    """
    checks if the current user is an instructor, and if so, logs them
    out if their account is confirmed.
    """
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
    """
    retrieves and returns information about the current user
    if they are an instructor.
    """
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


@app_views.route('/instructor/auth/create-class', methods=['POST'], strict_slashes=False)
@jwt_required()
def assign_instructor():
    """
    assigns students to an instructor for a specific course,
    semester, batch, and section.
    """
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        # testing line
        try:
            request.form = request.get_json()
            instructor_list = request.form.get('instructor_list', None)
            courses = request.form.get('courses', None)
            semister = request.form.get('semister', None)
            department = request.form.get('department', None)
            batch = request.form.get('batch', None)
            section = request.form.get('section', None)
            student_list = request.form.get('student_list', None)

            created_class = AssignedStudent.query.filter_by(semister=semister,
                                                            batch=batch,
                                                            department=department,
                                                            section=section).first()
            if created_class:
                return make_response(jsonify({'error': f'Class already exist for batch {batch} and section {section}',
                                             'created': False}), 400)
            response = {}
            created_class = AssignedStudent(semister=semister,
                                            batch=batch,
                                            department=department,
                                            section=section)
            for course in courses:
                created_class.courses.append(Course.query.filter_by(id=course['id']).first())
            for instructor in instructor_list:
                created_class.instructors.append(instructor_datastore.find_user(id=instructor['id']))
            for student in student_list:
                created_class.students.append(student_datastore.find_user(id=student['id']))
            db.session.add(created_class)
            db.session.commit()
            response['class'] = {
                'id': created_class.id,
                'year': created_class.year,
                'department': created_class.department,
                'semister': created_class.semister,
                'batch': created_class.batch,
                'section': created_class.section
                }
            response.update(
                students=[{'id': student.id} for student in created_class.students],
                instructors=[{'id': instructor.id} for instructor in created_class.instructors],
                courses=[{'id': course.id} for course in created_class.courses])
            return make_response(jsonify(response), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 400)
    return make_response(jsonify({'error': 'URL doesnt exist'}), 404)


@app_views.route('/instructor/auth/update-class/<id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_class(id):
    """
    function updates class details with instructor, course, and student information,
    and returns a JSON response.
    """
    admin_user, user_type = get_current_user()
    if user_type != 'admin':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    created_class = AssignedStudent.query.filter_by(id=id).first()
    if not created_class:
        return make_response(jsonify({'error': 'Assigned class no longer exists'}), 400)
    # testing purpose
    request.form = request.get_json()
    try:
        instructor_list = request.form.get('instructor_list', None)
        courses = request.form.get('courses', None)
        semister = request.form.get('semister', None)
        if semister is not None:
            created_class.semister = semister
        department = request.form.get('department', None)
        if department is not None:
            created_class.department = department
        batch = request.form.get('batch', None)
        if batch is not None:
            created_class.batch = batch
        section = request.form.get('section', None)
        if section is not None:
            created_class.section = section
        student_list = request.form.get('student_list', None)

        try:
            for course in courses:
                    created_class.courses.append(Course.query.filter_by(id=course['id']).first())
            for instructor in instructor_list:
                created_class.instructors.append(instructor_datastore.find_user(id=instructor['id']))
            for student in student_list:
                    created_class.students.append(student_datastore.find_user(id=student['id']))
        except Exception:
            pass
        db.session.add(created_class)
        db.session.commit()
        response = {}
        response['class'] = {
                'id': created_class.id,
                'year': created_class.year,
                'department': created_class.department,
                'semister': created_class.semister,
                'batch': created_class.batch,
                'section': created_class.section
                }
        response.update(
                students=[{'id': student.id} for student in created_class.students],
                instructors=[{'id': instructor.id} for instructor in created_class.instructors],
                courses=[{'id': course.id} for course in created_class.courses],
                updated=True)
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e), 'updated': False}), 400)
    

@app_views.route('/instructor/get-class/', methods=['GET'], strict_slashes=False)
def get_classes():
    """
    This Python function retrieves classes based on various parameters
    such as ID, instructor ID, student ID, batch, section, and course ID.
    """
    id = request.args.get('id', None)
    instructor_id = request.args.get('instructor_id', None)
    student_id = request.args.get('student_id', None)
    batch = request.args.get('batch', None)
    section = request.args.get('section', None)
    course_id = request.args.get('course_id', None)
    page = request.args.get('page', None)

    try:
        created_class = AssignedStudent.query
        if batch is not None:
            created_class = created_class.filter(AssignedStudent.batch == str(batch))
        if id is not None:
            created_class = created_class.filter(AssignedStudent.id == id)
        if section is not None:
            created_class = created_class.filter(AssignedStudent.section == section)
        if instructor_id is not None:
            created_class = created_class.join(Instructor,
                                               AssignedStudent.instructors).filter(Instructor.id == instructor_id)
        if student_id is not None:
            created_class = created_class.join(Student,
                                               AssignedStudent.students).filter(Student.id == student_id)
        if course_id is not None:
            created_class = created_class.join(Course,
                                               AssignedStudent.courses).filter(Course.id == course_id)
        responses = []
        response = {}
        if not created_class:
            return make_response(jsonify({'error': 'class not found'}), 404)
        created_class = created_class.all()
        # print(created_class)
        for classes in created_class:
            response['class'] = {
                        'id': classes.id,
                        'year': classes.year,
                        'department': classes.department,
                        'semister': classes.semister,
                        'batch': classes.batch,
                        'section': classes.section
                        }
            response.update(
                        students=[{'id': student.id} for student in classes.students],
                        instructors=[{'id': instructor.id} for instructor in classes.instructors],
                        courses=[{'id': course.id} for course in classes.courses])
            responses.append(response)
        return make_response(jsonify(responses), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/instructor/auth/delete-class/<id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_class(id):
    """
    deletes a class if the current user is an admin and the class exists,
    returning appropriate responses based on the outcome.
    """
    admin_user, user_type = get_current_user()
    if user_type != 'admin':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    created_class = AssignedStudent.query.filter_by(id=id).first()
    if not created_class:
        return make_response(jsonify({'error': 'class doesnt exist any more'}), 400)
    try:
        db.session.delete(created_class)
        db.session.commit()
        return make_response(jsonify({'deleted': True}), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)