#!/usr/bin/env python3

if __name__ == '__main__':
    from models.course import Course
    from models.instructor import Instructor
    from models.assigned_students import AssignedStudent
    from models.booked_room import Booked
    from models.instructor_session import InstAttendance
    from models.room import Room
    from models.student import Student
    from models.student_attendance import StuAttendance
    from models.admin_user import AdminUser
    from models import app, db, Role
    from flask_security import Security, SQLAlchemyUserDatastore
    from os import getenv


    app.config['SECRET_KEY'] = getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = getenv('SALT')


    with app.app_context():
        db.create_all()
        admin_datastore = SQLAlchemyUserDatastore(db, AdminUser, Role)
        app.security = Security(app, admin_datastore)
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
        db.session.commit()