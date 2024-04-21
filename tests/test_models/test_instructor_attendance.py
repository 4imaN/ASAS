#!/usr/bin/env python3

from models.instructor import Instructor
from models.room import Room
from models.instructor_session import InstAttendance
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
            'teacher_id': 'ETS0555/12',
            'email': 'test5@test.com',
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
            cls.session = InstAttendance(instructor_id=cls.instructor.id,
                                         room_id=cls.room.id,
                                         )
            db.session.add(cls.session)
            db.session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.session)
            db.session.delete(cls.instructor)
            db.session.delete(cls.room)
            db.session.commit()

    def test_session_data(self):
        """
        adds a session to the database and asserts the presence of
        specific attributes.
        """
        with app.app_context():
            db.session.add(self.session)
            db.session.add(self.instructor)
            db.session.add(self.room)
            self.assertTrue(getattr(self.session, 'instructor_id'))
            self.assertTrue(self.session.instructor_id == self.instructor.id)
            self.assertTrue(getattr(self.session, 'room_id'))
            self.assertTrue(self.session.room_id == self.room.id)
            self.assertTrue(getattr(self.session, 'start_time'))
            self.assertIsNone(self.session.end_time)
            self.assertTrue(type(self.session.start_time) is datetime)
