
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
    from models import app, db, Role, admin_datastore, \
        instructor_datastore, student_datastore
    from flask_security.utils import hash_password
    from datetime import datetime
    

    with app.app_context():
        db.create_all()

        admin_role = Role(name='admin', description='Access only to Administrator')
        instructor_role = Role(name='instructor', description='Access only to Instructor')
        student_role = Role(name='student', description='Access only to Student')
        password = hash_password('test_pwd')
        admin_user = AdminUser(first_name='test',
                               middle_name='test',
                               last_name='test',
                               gender='M',
                               email='test@test.com',
                               department='ECE',
                               password=password)
        admin_user.confirmed_at = datetime.now()
        admin_datastore.add_role_to_user(admin_user, admin_role)

        db.session.add(admin_role)
        db.session.add(instructor_role)
        db.session.add(student_role)
        admin_datastore.commit()
        instructor_datastore.commit()
        student_datastore.commit()
        db.session.commit()
