
from api.v1.views import app_views
from models import instructor_datastore, student_datastore
from flask import make_response, jsonify



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
