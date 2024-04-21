#!/usr/bin/env python3

from models.instructor import Instructor
from models.student import Student
from models.room import Room
from models.instructor_session import InstAttendance
from models.student_attendance import StuAttendance
from models.course import Course
from models import db, app
from datetime import datetime
import unittest
import bcrypt


class TestInstructorSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.instructor_data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'teacher_id': 'ETS0777/12',
            'email': 'test6@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'qualification': 'Masters in Electrical Eng.'
        }
        cls.student_data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'registered': False,
            'student_id': 'ETS0001/12',
            'email': 'test8@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'batch_section': '2012 A',
        }
        cls.room_data = {
            'block_no': 'B54',
            'room_no': '3009'
        }
        cls.course_data = {
            'course_code': 'ECEF_452',
            'course_name': 'DLD',
            'course_credit': '4',
            'course_category': 'Major',
        }
        cls.instructor = Instructor(**cls.instructor_data)
        cls.student = Student(**cls.student_data)
        cls.room = Room(**cls.room_data)
        cls.course = Course(**cls.course_data)
        with app.app_context():
            db.session.add(cls.instructor)
            db.session.add(cls.room)
            db.session.add(cls.course)
            db.session.add(cls.student)
            db.session.commit()
            cls.session = InstAttendance(instructor_id=cls.instructor.id,
                                         room_id=cls.room.id,
                                         )
            db.session.add(cls.session)
            db.session.commit()
            cls.studentAtt = StuAttendance(session_id=cls.session.id,
                                           course_id=cls.course.id,
                                           student_id=cls.student.id,
                                           instructor_id=cls.instructor.id,
                                           room_id=cls.room.id,
                                           )
            db.session.add(cls.studentAtt)
            db.session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.studentAtt)
            db.session.delete(cls.session)
            db.session.delete(cls.instructor)
            db.session.delete(cls.room)
            db.session.delete(cls.course)
            db.session.delete(cls.student)
            db.session.commit()

    def test_attendance_data(self):
        """
        adds an attendance to the database and asserts the presence of
        specific attributes.
        """
        with app.app_context():
            db.session.add(self.session)
            db.session.add(self.instructor)
            db.session.add(self.room)
            db.session.add(self.studentAtt)
            self.assertTrue(getattr(self.studentAtt, 'instructor_id'))
            self.assertTrue(self.studentAtt.instructor_id == self.instructor.id)
            self.assertTrue(getattr(self.studentAtt, 'room_id'))
            self.assertTrue(self.studentAtt.room_id == self.room.id)
            self.assertTrue(getattr(self.studentAtt, 'start_time'))
            self.assertIsNone(self.studentAtt.end_time)
            self.assertTrue(type(self.studentAtt.start_time) is datetime)
