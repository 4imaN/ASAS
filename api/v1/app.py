#!/usr/bin/env python3
from models import db, app
from flask import jsonify, make_response
from flask_cors import CORS
from api.v1.views import app_views



CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})
app.register_blueprint(app_views)


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

