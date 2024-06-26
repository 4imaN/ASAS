

from models.student import Student
from models import db, app
from datetime import datetime
import unittest
import bcrypt


class TestStudent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = {
            'first_name': 'test_1',
            'middle_name': 'test_1',
            'last_name': 'test_1',
            'gender': 'M',
            'registered': False,
            'student_id': 'ETS0111/12',
            'email': 'test@test.com',
            'department': 'ECE',
            'password': bcrypt.hashpw('test_pwd'.encode(), bcrypt.gensalt()),
            'batch_section': '2012 A',
        }
        cls.student = Student(**cls.data)
        with app.app_context():
            db.session.add(cls.student)
            db.session.commit()


    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.student)
            db.session.commit()

    def test_student_data(self):
        """
        adds a student to the database and asserts the presence of
        specific attributes for the student.
        """
        with app.app_context():
            db.session.add(self.student)
            self.assertTrue(getattr(self.student, 'first_name'))
            self.assertTrue(getattr(self.student, 'middle_name'))
            self.assertTrue(getattr(self.student, 'last_name'))
            self.assertTrue(getattr(self.student, 'gender'))
            self.assertTrue(getattr(self.student, 'email'))
            self.assertTrue(getattr(self.student, 'password'))

    def test_student_email(self):
        """
        tests if a student's email is valid by checking for presence.
        """
        with app.app_context():
            db.session.add(self.student)
            self.assertEqual(self.student.email, self.data['email'])
            self.assertIn("@", self.student.email)
            self.assertIn(".com", self.student.email)

    def test_student_password(self):
        """
        adds a student to the database session and compares the encoded
        password with the provided password data.
        """
        with app.app_context():
            db.session.add(self.student)
            self.assertEqual(self.student.password.encode(), self.data['password'])

    def test_update_time(self):
        """
        tests if the `updated_at` time of a student object is correctly
        updated when the student's field is changed.
        """
        with app.app_context():
            db.session.add(self.student)
            updated_time = datetime.strptime(self.student.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.student.registered = True
            db.session.commit()
            new_time = datetime.strptime(self.student.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.assertTrue(new_time > updated_time)
