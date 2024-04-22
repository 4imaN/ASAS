#!/usr/bin/env python3

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


admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Instructor, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(AssignedStudent, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(StuAttendance, db.session))
admin.add_view(ModelView(Booked, db.session))
admin.add_view(ModelView(AdminUser, db.session))
admin.add_view(ModelView(InstAttendance, db.session))
