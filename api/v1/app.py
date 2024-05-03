
from models import db, app, instructor_datastore, \
    admin_datastore, student_datastore
from flask import jsonify, make_response, session, request
from flask_cors import CORS
from api.v1.views import app_views
from flask_security import Security
from flask_jwt_extended import get_current_user, jwt_required, verify_jwt_in_request



CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})
app.register_blueprint(app_views)


# @app.before_request
# def check_user():
#     try:
#         verify_jwt_in_request(locations=['headers'])
#         user, user_type = get_current_user()
#         print(session)
#     #     if user_type == 'admin':
#     #         print(0)
#     #         security = Security(app, datastore=admin_datastore,
#     #                           register_blueprint=False)
#     #     elif user_type == 'instructor':
#     #         print(1)
#     #         security.init_app(app, datastore=instructor_datastore,
#     #                           register_blueprint=False)
#     #     elif user_type == 'student':
#     #         print(2)
#     #         security.init_app(app, datastore=student_datastore,
#     #                           register_blueprint=False)
#     except Exception as e:
#         print(e)
#         return
#     pass


@app.teardown_appcontext
def tear_down_db(exc):
    """
    The function `tear_down_db` closes the database session.
    """
    db.session.close()


@app.errorhandler(404)
def error_404(err):
    """
    returns a response with a JSON object with an error message
    for a 404 Not Found status code.
    """
    return make_response(jsonify({'message': str(err)}), 404)


@app.errorhandler(401)
def error_401(err):
    """
    returns a response with a JSON object with an error message.
    """
    return make_response(jsonify({'message': str(err)}), 401)


@app.errorhandler(400)
def error_400(err):
    """
    returns a response with a JSON object with an error message.
    """
    return make_response(jsonify({'message': str(err)}), 400)

@app.errorhandler(422)
def error_422(err):
    """
    returns a response with a JSON object with an error message.
    """
    return make_response(jsonify({'message': str(err)}), 422)

@app.errorhandler(415)
def error_415(err):
    """
    returns a response with a JSON object with an error message.
    """
    return make_response(jsonify({'message': str(err)}), 415)



if __name__ == '__main__':
    # use env var for the host and port 
    app.run(host='0.0.0.0',
            port=5000, debug=True)

