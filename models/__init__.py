

from flask_admin.contrib.sqla import ModelView
from models.basemodel import app, db, admin, Role
from models.student import Student
from models.instructor import Instructor
from models.course import Course
from models.room import Room
from models.booked_room import Booked
from models.assigned_students import AssignedStudent
from models.student_attendance import StuAttendance
from models.admin_user import AdminUser
from models.instructor_session import InstAttendance
from flask_security import Security, SQLAlchemyUserDatastore, current_user
# from wtforms.ext.sqlalchemy.fields import QuerySelectField
from os import getenv
# import logging


app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = getenv('SALT')
app.config['SECURITY_TRACKABLE'] = True
app.config['SESSION_TYPE'] = 'cookie'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['DEFAULT_REMEMBER_ME'] = True
app.config['JWT_SECRET_KEY'] = getenv('SECRET_KEY')
app.config['BLUEPRINT_NAME'] = 'instructor_security'



admin_datastore = SQLAlchemyUserDatastore(db, AdminUser, Role)
instructor_datastore = SQLAlchemyUserDatastore(db, Instructor, Role)
student_datastore = SQLAlchemyUserDatastore(db, Student, Role)

security = Security(app, datastore=admin_datastore)





class NewView(ModelView):
    # flask admin panel
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
        # return True
# class AssignedStudentModelView(ModelView):
#     # Customize the form to use a dropdown for course_id
#     form_overrides = {
#         'course_id': QuerySelectField
#     }
    
#     # Define a query to populate the dropdown
#     def form_widget_args(self):
#         return {
#             'course_id': {
#                 'query_factory': lambda: Course.query.all(),
#                 'allow_blank': True,
#                 'blank_text': 'Select a Course'
#             }
#         }

#     # Specify columns to display in list view
#     column_list = ('id', 'student_name', 'course')

#     # Optionally, specify form columns if you want to include/exclude specific fields
#     form_columns = ('student_name', 'course_id')


admin.add_view(NewView(Student, db.session))
admin.add_view(NewView(Instructor, db.session))
admin.add_view(NewView(Room, db.session))
admin.add_view(NewView(AssignedStudent, db.session))
admin.add_view(NewView(Course, db.session))
admin.add_view(NewView(StuAttendance, db.session))
admin.add_view(NewView(Booked, db.session))
admin.add_view(NewView(AdminUser, db.session))
admin.add_view(NewView(InstAttendance, db.session))
