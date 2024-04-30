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
    

    with app.app_context():
        db.create_all()
        admin_role = Role(name='admin', description='Access only to Administrator')
        teacher_role = Role(name='instructor', description='Access only to Instructor')
        db.session.add(admin_role)
        db.session.add(teacher_role)
        db.session.commit()