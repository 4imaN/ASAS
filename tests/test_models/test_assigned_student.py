#!/usr/bin/env python3

from models.student import Student
from models.instructor import Instructor
from models.course import Course
from models.assigned_students import AssignedStudent
from datetime import datetime
from models import db, app
import unittest
import bcrypt


class TestAssignedStudent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.student_data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'registered': False,
            'student_id': 'ETS0333/12',
            'email': 'test3@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'batch_section': '2012 A',
        }
        cls.instructor_data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'teacher_id': 'ETS0444/12',
            'email': 'test4@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'qualification': 'Masters in Electrical Eng.'
        }
        cls.course_data = {
            'course_code': 'ECED_452',
            'course_name': 'DLD',
            'course_credit': '4',
            'course_category': 'Major',
        }
        cls.student = Student(**cls.student_data)
        cls.instructor = Instructor(**cls.instructor_data)
        cls.course = Course(**cls.course_data)
        with app.app_context():
            db.session.add(cls.student)
            db.session.add(cls.instructor)
            db.session.add(cls.course)
            db.session.commit()
            cls.assigned = AssignedStudent(student_id=cls.student.id,
                                           instructor_id=cls.instructor.id,
                                           course_id=cls.course.id)
            db.session.add(cls.assigned)
            db.session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.assigned)
            db.session.delete(cls.student)
            db.session.delete(cls.instructor)
            db.session.delete(cls.course)
            db.session.commit()

    def test_assigned_data(self):        
        """
        checks if the assigned data contains necessary attributes and
        timestamps.
        """
        with app.app_context():
            db.session.add(self.student)
            db.session.add(self.instructor)
            db.session.add(self.course)
            db.session.add(self.assigned)
            self.assertTrue(getattr(self.assigned, 'student_id'))
            self.assertIn('student', dir(self.assigned))
            self.assertTrue(getattr(self.assigned, 'instructor_id'))
            self.assertIn('instructor', dir(self.assigned))
            self.assertTrue(getattr(self.assigned, 'course_id'))
            self.assertIn('course', dir(self.assigned))
            created_at = datetime.strptime(self.assigned.created_at, "%Y-%m-%d %H:%M:%S.%f")
            updated_at = datetime.strptime(self.assigned.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.assertTrue(updated_at > created_at)
