

from models.instructor import Instructor
from models.student import Student
from models.room import Room
from models.booked_room import Booked
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
            'teacher_id': 'ETS0888/12',
            'email': 'test9@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'qualification': 'Masters in Electrical Eng.'
        }
        cls.room_data = {
            'block_no': 'B54',
            'room_no': '3009'
        }

        cls.instructor = Instructor(**cls.instructor_data)
        cls.room = Room(**cls.room_data)
        with app.app_context():
            db.session.add(cls.instructor)
            db.session.add(cls.room)
            db.session.commit()
            cls.booked = Booked(instructor_id=cls.instructor.id,
                                room_id=cls.room.id)
            db.session.add(cls.booked)
            db.session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.booked)
            db.session.delete(cls.instructor)
            db.session.delete(cls.room)
            db.session.commit()

    def test_booked_room_data(self):
        """
        adds a booked object to the database and asserts the presence of
        specific attributes.
        """
        with app.app_context():
            db.session.add(self.instructor)
            db.session.add(self.room)
            db.session.add(self.booked)
            self.assertTrue(getattr(self.booked, 'instructor_id'))
            self.assertTrue(self.booked.instructor_id == self.instructor.id)
            self.assertTrue(getattr(self.booked, 'room_id'))
            self.assertTrue(self.booked.room_id == self.room.id)
