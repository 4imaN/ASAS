
from models import admin_datastore, Course, app, db
from flask_jwt_extended import get_current_user, jwt_required
from api.v1.views import app_views
from flask import make_response, jsonify, request


@app_views.route('/course/auth/create', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_course():
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        # testing line
        request.form = request.get_json()
        course_code = request.form.get('course_code', None)
        course_name = request.form.get('course_name', None)
        course_credit = request.form.get('course_credit', None)
        course_department = request.form.get('course_department', None)
        course_category = request.form.get('course_category', None)
        course = Course.query.filter_by(course_code=course_code).first()
        if course:
            return make_response(jsonify({'error': 'Course already exists'}), 400)
        try:
            course = Course(course_code=course_code,
                            course_name=course_name,
                            course_credit=course_credit,
                            course_department=course_department,
                            course_category=course_category)
            db.session.add(course)
            db.session.commit()
            return make_response(jsonify({'course_code': course.course_code,
                            'course_name': course.course_name,
                            'course_credit': course.course_credit,
                            'course_department': course.course_department,
                            'course_category': course.course_category,
                            'created': True}), 201)
        except Exception as e:
            return make_response(jsonify({'error': str(e), 'created': False}), 400)
    return make_response(jsonify({'error': 'url doesnt exist'}), 404)


@app_views.route('/course/update/<id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_course(id):
    admin_user, user_type = get_current_user()
    if user_type == 'admin':
        # testing line
        course = Course.query.filter_by(id=id).first()
        if course:
            updatables = ['course_code', 'course_name',
                          'course_credit', 'course_category',
                          'course_department']
            data = request.get_json()
            for k in data.keys():
                    if k not in updatables:
                        return jsonify({'error': f'key {k} not updatable or not available'}), 400
            for k, v in data.items():
                    setattr(course, k, v)
            db.session.add(course)
            db.session.commit()
            res_dict = {k: getattr(course, k) for k in updatables if k in data.keys()}
            res_dict.update({'updated': True})
            return make_response(jsonify(res_dict), 200)
    return make_response(jsonify({'error': 'url doesnt exist'}), 404)


@app_views.route('/course/getid/<id>', methods=['GET'], strict_slashes=False)
def get_course_id(id):
     course = Course.query.filter_by(id=id).first()
     if not course:
          return make_response(jsonify({'error': 'course not found'}), 400)
     return make_response(jsonify({'course_code': course.course_code,
                            'course_name': course.course_name,
                            'course_credit': course.course_credit,
                            'course_department': course.course_department,
                            'course_category': course.course_category}), 200)


@app_views.route('/course/getdep/<department>', methods=['GET'], strict_slashes=False)
def get_course_dep(department):
    courses = Course.query.filter_by(course_department=department).all()
    if not courses or courses == []:
        return make_response(jsonify({'error': 'no courses found'}), 404)
    all_courses = []
    for course in courses:
        if get_course_id(course.id).status_code == 200:
            all_courses.append(get_course_id(course.id).json)
    return make_response(jsonify(all_courses), 200)


@app_views.route('/course/getcred/<credit>', methods=['GET'], strict_slashes=False)
def get_course_credit(credit):
     courses = Course.query.filter_by(course_credit=credit).all()
     if not courses or courses == []:
          return make_response(jsonify({'error': 'no courses found'}), 404)
     all_courses = []
     for course in courses:
        if get_course_id(course.id).status_code == 200:
            all_courses.append(get_course_id(course.id).json)
     return make_response(jsonify(all_courses), 200)


@app_views.route('/course/getcat/<category>', methods=['GET'], strict_slashes=False)
def get_course_category(category):
     courses = Course.query.filter_by(course_category=category).all()
     if not courses or courses == []:
          return make_response(jsonify({'error': 'no courses found'}), 404)
     all_courses = []
     for course in courses:
        if get_course_id(course.id).status_code == 200:
            all_courses.append(get_course_id(course.id).json)
     return make_response(jsonify(all_courses), 200)


@app_views.route('/course/get/<name>', methods=['GET'], strict_slashes=False)
def get_course_name(name):
     courses = Course.query.filter_by(course_name=name).all()
     if not courses or courses == []:
          return make_response(jsonify({'error': 'no courses found'}), 404)
     all_courses = []
     for course in courses:
          if get_course_id(course.id).status_code == 200:
             all_courses.append(get_course_id(course.id).json)
     return make_response(jsonify(all_courses), 200)
