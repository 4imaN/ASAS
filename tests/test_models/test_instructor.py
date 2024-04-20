#!/usr/bin/env python3

from models.instructor import Instructor
from models import db, app
import unittest
import bcrypt


class TestInstructor(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'teacher_id': 'ETS0222/12',
            'email': 'test2@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'qualification': 'Masters in Electrical Eng.'
        }
        cls.instructor = Instructor(**cls.data)
        with app.app_context():
            db.session.add(cls.instructor)
            db.session.commit()


    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.instructor)
            db.session.commit()

    def test_instructor_data(self):
        """
        adds a instructor to the database and asserts the presence of
        specific attributes for the instructor.
        """
        with app.app_context():
            db.session.add(self.instructor)
            self.assertTrue(getattr(self.instructor, 'first_name'))
            self.assertTrue(getattr(self.instructor, 'middle_name'))
            self.assertTrue(getattr(self.instructor, 'last_name'))
            self.assertTrue(getattr(self.instructor, 'gender'))
            self.assertTrue(getattr(self.instructor, 'email'))
            self.assertTrue(getattr(self.instructor, 'password'))

    def test_instructor_email(self):
        """
        tests if a instructor's email is valid by checking for presence.
        """
        with app.app_context():
            db.session.add(self.instructor)
            self.assertEqual(self.instructor.email, self.data['email'])
            self.assertIn("@", self.instructor.email)
            self.assertIn(".com", self.instructor.email)

    def test_instructor_password(self):
        """
        adds a instructor to the database session and compares the encoded
        password with the provided password data.
        """
        with app.app_context():
            db.session.add(self.instructor)
            self.assertEqual(self.instructor.password.encode(), self.data['password'])
