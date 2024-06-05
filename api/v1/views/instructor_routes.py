
from models import db, instructor_datastore, \
    admin_datastore, student_datastore, AssignedStudent, Course, \
    Instructor, Student, Booked, Room, InstAttendance, StuAttendance
from flask import jsonify, request, make_response
from datetime import datetime, timedelta
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from flask_security import auth_required, login_user, logout_user, \
    roles_required, current_user, roles_accepted
from flask_security.utils import hash_password, verify_password
from flask_jwt_extended import get_current_user, jwt_required, unset_access_cookies, create_access_token
from utils.mailer import Mailer
from requests import get
from api.v1.views import app_views
from utils.schedules import delete_records
import time


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
            res = make_response(jsonify({'msg': True, "access_token": access_token}), 200)
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
                        return make_response(jsonify({'error': f'key {k} not updatable or not available'}), 400)
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
@jwt_required()
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
                                      'id': instructor.id
                                      }), 200)
    return make_response(jsonify({'error': 'URL doesnt exist'}), 404)


@app_views.route('/instructor/my-courses', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_instructor_course():
    instructor, user_type = get_current_user()
    if user_type != 'instructor':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    try:
        courses = []
        for course in instructor.courses:
            courses.append({
                'id': course.id,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'course_credit': course.course_credit,
                'course_category': course.course_category,
                'course_department': course.course_department
            })
        return make_response(jsonify(courses), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


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
            instructor_id = request.form.get('instructor_id', None)
            course_id = request.form.get('course_id', None)
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
            try:
                for student in student_list:
                    created_class.students.append(student_datastore.find_user(id=student['id']))
                if Course.query.filter_by(id=course_id).first():
                    created_class.courses.append(Course.query.filter_by(id=course_id).first())
                if instructor_datastore.find_user(id=instructor_id):
                    created_class.instructors.append(instructor_datastore.find_user(id=instructor_id))
                    instructor_datastore.find_user(id=instructor_id).courses.append(Course.query.filter_by(id=course_id).first())
            except Exception:
                pass
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
                students=[{'id': student.id,
                           'first_name': student.first_name,
                           'middle_name': student.middle_name,
                           'last_name': student.last_name,
                           'email': student.email,
                           'gender': student.gender,
                           'department': student.department,
                           'batch': str(student.batch_section).split(" ")[0],
                           'section': str(student.batch_section).split(" ")[1]} for student in created_class.students],
                instructors=[{'id': instructor.id,
                            'first_name': instructor.first_name,
                           'middle_name': instructor.middle_name,
                           'last_name': instructor.last_name,
                           'email': instructor.email,
                           'qualification': instructor.qualification,
                           'courses': [{'id': course.id,
                                        'name': course.course_name,
                                        'credit': course.course_credit,
                                        'category': course.course_category,
                                        'course_department': course.course_department,
                                        'course_code': course.course_code} for course in instructor.courses],
                           'department': instructor.department,} for instructor in created_class.instructors],
                courses=[{'id': course.id,
                          'name': course.course_name,
                          'credit': course.course_credit,
                          'category': course.course_category,
                          'course_department': course.course_department,
                          'course_code': course.course_code} for course in created_class.courses])
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
        instructor_id = request.form.get('instructor_id', None)
        course_id = request.form.get('course_id', None)
        semister = request.form.get('semister', None)
        # if semister is not None:
        #     created_class.semister = semister
        department = request.form.get('department', None)
        # if department is not None:
        #     created_class.department = department
        batch = request.form.get('batch', None)
        # if batch is not None:
        #     created_class.batch = batch
        section = request.form.get('section', None)
        # if section is not None:
        #     created_class.section = section
        student_list = request.form.get('student_list', None)

        try:
            class_instructor_id = [i.id for i in created_class.instructors]
            if instructor_id not in class_instructor_id:
                created_class.instructors.append(instructor_datastore.find_user(id=instructor_id))
            class_course_id = [i.id for i in created_class.courses]
            if course_id not in class_course_id:
                instructor_datastore.find_user(id=instructor_id).courses.append(Course.query.filter_by(id=course_id).first())
                created_class.courses.append(Course.query.filter_by(id=course_id).first())
            for student in student_list:
                    class_students_id = [i.id for i in created_class.students]
                    if student.id not in class_students_id:
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
                students=[{'id': student.id,
                           'first_name': student.first_name,
                           'middle_name': student.middle_name,
                           'last_name': student.last_name,
                           'email': student.email,
                           'gender': student.gender,
                           'department': student.department,
                           'batch': str(student.batch_section).split(" ")[0],
                           'section': str(student.batch_section).split(" ")[1]} for student in created_class.students],
                instructors=[{'id': instructor.id,
                            'first_name': instructor.first_name,
                           'middle_name': instructor.middle_name,
                           'last_name': instructor.last_name,
                           'email': instructor.email,
                           'qualification': instructor.qualification,
                           'courses': [{'id': course.id,
                                        'name': course.course_name,
                                        'credit': course.course_credit,
                                        'category': course.course_category,
                                        'course_department': course.course_department,
                                        'course_code': course.course_code} for course in instructor.courses if course.id in class_course_id],
                           'department': instructor.department,} for instructor in created_class.instructors],
                courses=[{'id': course.id,
                          'name': course.course_name,
                          'credit': course.course_credit,
                          'category': course.course_category,
                          'course_department': course.course_department,
                          'course_code': course.course_code} for course in created_class.courses], updated=True)
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e), 'updated': False}), 400)
    

@app_views.route('/instructor/get-class/', methods=['GET'], strict_slashes=False)
# @jwt_required()
def get_classes():
    """
    This Python function retrieves classes based on various parameters
    such as ID, instructor ID, student ID, batch, section, and course ID.
    """
    # user, user_type = get_current_user()
    # if user_type not in ['admin', 'instructor']:
    #     return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    id = request.args.get('id', None)
    instructor_id = request.args.get('instructor_id', None)
    student_id = request.args.get('student_id', None)
    batch = request.args.get('batch', None)
    section = request.args.get('section', None)
    course_id = request.args.get('course_id', None)
    department = request.args.get('department', None)
    year = request.args.get('year', None)
    page = request.args.get('page', None)

    try:
        created_class = AssignedStudent.query
        if batch is not None:
            created_class = created_class.filter(AssignedStudent.batch == str(batch))
        if id is not None:
            created_class = created_class.filter(AssignedStudent.id == id)
        if year is not None:
            created_class = created_class.filter(AssignedStudent.year == year)
        if section is not None:
            created_class = created_class.filter(AssignedStudent.section == section)
        if instructor_id is not None:
            created_class = created_class.join(Instructor,
                                               AssignedStudent.instructors).filter(Instructor.id == instructor_id)
        if student_id is not None:
            created_class = created_class.join(Student,
                                               AssignedStudent.students).filter(Student.id == student_id)
        if department is not None:
            created_class = created_class.filter(AssignedStudent.department == department)
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
            class_course_id = [i.id for i in classes.courses]
            response['class'] = {
                        'id': classes.id,
                        'year': classes.year,
                        'department': classes.department,
                        'semister': classes.semister,
                        'batch': classes.batch,
                        'section': classes.section
                        }
            response.update(
                students=[{'id': student.id,
                           'first_name': student.first_name,
                           'middle_name': student.middle_name,
                           'last_name': student.last_name,
                           'email': student.email,
                           'gender': student.gender,
                           'department': student.department,
                           'batch': str(student.batch_section).split(" ")[0],
                           'section': str(student.batch_section).split(" ")[1]} for student in classes.students],
                instructors=[{'id': instructor.id,
                            'first_name': instructor.first_name,
                           'middle_name': instructor.middle_name,
                           'last_name': instructor.last_name,
                           'email': instructor.email,
                           'qualification': instructor.qualification,
                           'courses': [{'id': course.id,
                                        'name': course.course_name,
                                        'credit': course.course_credit,
                                        'category': course.course_category,
                                        'course_department': course.course_department,
                                        'course_code': course.course_code} for course in instructor.courses if course.id in class_course_id],
                           'department': instructor.department,} for instructor in classes.instructors],
                courses=[{'id': course.id,
                          'name': course.course_name,
                          'credit': course.course_credit,
                          'category': course.course_category,
                          'course_department': course.course_department,
                          'course_code': course.course_code} for course in classes.courses])
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


@app_views.route('/instructor/auth/create-session', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_class_session():
    instructor_user, user_type = get_current_user()
    if user_type != 'instructor':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    # testing purpose
    request.form = request.get_json()
    room_id = request.form.get('room_id', None)
    course_id = request.form.get('course_id', None)
    student_list = request.form.get('student_list', None)
    start_time = request.form.get('start_time', None)
    if not Room.query.filter_by(id=room_id).first():
        return make_response(jsonify({'error': 'No room found'}), 400)
    try:
        start_time = int(start_time)
        minutes = start_time - 10
    except (ValueError, TypeError):
        return make_response(jsonify({'error': 'time must be Integer'}), 400)
    try:
        # check if a room is already occupied
        is_booked = Booked.query.filter_by(id=id).first()
        if is_booked and not is_booked.over:
            return make_response(jsonify({'error': f'book already occupied at {is_booked.created_at}'}), 400)

        # check if instructor already occupied a room
        already_sessions = InstAttendance.query.filter_by(instructor_id=instructor_user.id).all()
        for instructor_session in already_sessions:
            if not instructor_session.end_time:
                return make_response(jsonify(
                    {'error': f'Instructor already have a session created at {instructor_session.start_time} if you wish to create new session remove previous session'}), 400)
        # check if the students is registered for the course and instructor
        # student_in_course = False
        # student_of_instructor = False
        # i = 0
        # for s_id in student_list:
        #     student_class = AssignedStudent.query.join(Student,
        #                                                AssignedStudent.students).filter(Student.id == s_id['id']).first()
        #     for instructor, course in zip(student_class.instructors, student_class.courses):
        #         if student_in_course and student_of_instructor:
        #             break
        #         if instructor.id == instructor_user.id:
        #             student_of_instructor = True
        #         if course.id == course_id:
        #             student_in_course = Tru           e
        #     if not student_of_instructor:
        #         del student_list[i]
        #         i += 1
        #         continue
        #     if not student_in_course:
        #         del student_list[i]
        #         i += 1
        #         continue
        #     i += 1
        # starting to create session with start_time
        # need to configure celery
        start_time = datetime.now() + timedelta(minutes=start_time)
        instructor_session = InstAttendance(instructor_id=instructor_user.id,
                                            course_id=course_id,
                                            room_id=room_id,
                                            start_time=start_time)
        db.session.add(instructor_session)
        db.session.commit()
        for student in student_list:
            stu_attende = StuAttendance(session_id=instructor_session.id,
                                        course_id=course_id,
                                        student_id=student,
                                        instructor_id=instructor_user.id,
                                        room_id=room_id,
                                        start_time=start_time)
            db.session.add(stu_attende)
            db.session.commit()
            instructor_session.student_attendance.append(stu_attende)
        booked_room = Booked(instructor_id=instructor_user.id,
                             room_id=room_id)
        db.session.add(instructor_session)
        db.session.add(booked_room)
        db.session.commit()
        response = {}
        response['session'] = {
            'instructor_id': instructor_session.instructor_id,
            'course_id': instructor_session.course_id,
            'room_id': instructor_session.room_id,
            'students':[{'id': student.student_id} for student in list(instructor_session.student_attendance)]
        }
        response['msg'] = True
        delete_records.apply_async(args=(start_time, instructor_session.id), countdown=minutes*60)
        return make_response(jsonify(response), 201)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/instructor/verify-session/<session_id>', methods=['PUT'], strict_slashes=False)
# @jwt_required()
def verify_session_instructor(session_id):
    # instructor, user_type = get_current_user()
    # if user_type != 'instructor':
    #     return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    try:
        session = InstAttendance.query.filter_by(id=session_id).first()
    except Exception:
        return make_response(jsonify({'error': 'Session not found'}), 404)
    if not session:
        return make_response(jsonify({'error': 'No class session found'}), 400)
    uri = 'http://localhost:5000/api/v1'
    # test
    request.form = request.get_json()
    finger_id = request.form.get('finger_id', None)
    rf_id = request.form.get('rf_id', None)
    verified = False
    data = None
    try:
        if finger_id:
            data = get(f'{uri}/instructor/fingerid/{finger_id}').json
            if data['verified']:
                if data['instructor_id'] == session.instructor_id:
                    session.verified = True
                    db.session.add(session)
                    db.session.commit()

                    verified = True
                    return make_response(jsonify({'verified': verified}), 200)
        if rf_id:
            data = get(f'{uri}/instructor/rfid/{rf_id}').json
            if data['verified']:
                if data['instructor_id'] == session.instructor_id:
                    session.verified = True
                    db.session.add(session)
                    db.session.commit()

                    verified = True        
                    return make_response(jsonify({'verified': verified}), 200)
        return make_response(jsonify({'verified': verified}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/instructor/get-session', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_instructor_session():
    try:
        instructor, user_type = get_current_user()
        if user_type != 'instructor':
            return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
        sessions = InstAttendance.query.filter_by(instructor_id=instructor.id).all()
        response = {}
        for session in sessions:
            if not session.verified:
                student_id = session.student_attendance[0].student_id
                student_class = AssignedStudent.query
                student_class = student_class.filter(AssignedStudent.year == datetime.now().year)
                student_class = student_class.join(Student, AssignedStudent.students).filter(Student.id == student_id)
                response['msg'] = True
                response['session'] = {'course_name': Course.query.filter_by(id=session.course_id).first().course_name,
                                    'room': Room.query.filter_by(id=session.room_id).first().block_no + " "  + Room.query.filter_by(id=session.room_id).first().room_no,
                                    'start_time': F"{session.start_time.day}/{session.start_time.month}/{session.start_time.year} {session.start_time.hour}:{session.start_time.minute}",
                                    'instructor_id': instructor.id,
                                    'department': student_class.year,
                                    'academic_year': student_class.year,
                                    'semister': student_class.semister,
                                    'batch': student_class.batch,
                                    'section': student_class.section
                                    }
                return make_response(jsonify(response), 200)
        return make_response(jsonify({'msg': False}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e), 'msg': False}), 400)


@app_views.route("/instructor/in-class", methods=['GET'], strict_slashes=False)
@jwt_required()
def check_instructor_class():
    instructor, user_type = get_current_user()
    if user_type != 'instructor':
        return make_response(jsonify({"error": "URL doesnt exist"}), 404)
    try:
        sessions = InstAttendance.query.filter(InstAttendance.instructor_id == instructor.id)
        sessions = sessions.filter(InstAttendance.verified == False)
        try:
            sessions = sessions.all()[0]
            if sessions:
                return make_response(jsonify({'msg': False}), 200)
        except Exception:
            pass
        sessions = InstAttendance.query.filter(InstAttendance.instructor_id == instructor.id)
        sessions = sessions.all()
        response = []
        for session in sessions:
            if session.verified and not session.end_time:
                student_attendance = session.student_attendance
                for stu_att in student_attendance:
                    arrived_time = stu_att.arrived_time if stu_att.arrived_time else "X"
                    student = student_datastore.find_user(id=stu_att.student_id)
                    response.append({
                        'arrived_time': arrived_time,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'middle_name': student.middle_name,
                        'email': student.email,
                        'student_id': student.student_id,
                        'id': student.id
                    })
                return make_response(jsonify(response), 200)
        return make_response(jsonify({'msg': False, "error": "no open session found"}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app_views.route('/instructor/auth/delete-session/', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_session():
    instructor, user_type = get_current_user()
    if user_type != 'instructor':
        return make_response(jsonify({'error': 'URL doesnt exist'}), 404)
    # test
    # request.form = request.get_json()
    # finger_id = request.form.get('finger_id', None)
    # rf_id = request.form.get('rf_id', None)
    try:
        sessions = InstAttendance.query.filter_by(instructor_id=instructor.id).all()
        response = {}
        for session in sessions:
            if not session.verified:
                # response['msg'] = True
                response['session'] = {'course_name': Course.query.filter_by(id=session.course_id).first().course_name,
                                    'room': Room.query.filter_by(id=session.room_id).first().block_no + " "  + Room.query.filter_by(id=session.room_id).first().room_no,
                                    'start_time': F"{session.start_time.day}/{session.start_time.month}/{session.start_time.year} {session.start_time.hour}:{session.start_time.minute}",
                                    'deleted': True
                                    }
                db.session.delete(session)
                db.session.commit()
                return make_response(jsonify(response), 200)
        return make_response(jsonify({'deleted': False}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
    
