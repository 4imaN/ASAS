#!/usr/bin/env python3
from models import db, app, AdminUser, Instructor, Student
from flask_jwt_extended import JWTManager
from datetime import timedelta
import redis




ACCESS_EXPIRES = timedelta(hours=1)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
jwt = JWTManager(app)

jwt_redis_blocklist = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True
)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    identity = jwt_data['sub']
    user_type = jwt_data['type']
    if user_type == 'admin':
        user = AdminUser.query.filter_by(id=identity).first()
    if user_type == 'instructor':
        user = Instructor.query.filter_by(id=identity).first()
    if user_type == 'student':
        user = Student.query.filter_by(id=identity).first()
    return user, user_type
