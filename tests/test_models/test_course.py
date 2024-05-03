

from models.course import Course
from models import db, app
from datetime import datetime
import unittest


class TestCourse(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = {
            'course_code': 'ECEG_452',
            'course_name': 'DLD',
            'course_credit': '4',
            'course_category': 'Major',
        }
        cls.course = Course(**cls.data)
        with app.app_context():
            db.session.add(cls.course)
            db.session.commit()


    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.course)
            db.session.commit()

    def test_course_data(self):
        """
        adds a course to the database and asserts the presence of
        specific attributes for the course.
        """
        with app.app_context():
            db.session.add(self.course)

            self.assertTrue(getattr(self.course, 'course_code'))
            self.assertEqual(self.course.course_code, self.data['course_code'])

            self.assertTrue(getattr(self.course, 'course_name'))
            self.assertEqual(self.course.course_name, self.data['course_name'])

            self.assertTrue(getattr(self.course, 'course_credit'))
            self.assertEqual(self.course.course_credit, self.data['course_credit'])

            self.assertTrue(getattr(self.course, 'course_category'))
            self.assertEqual(self.course.course_category, self.data['course_category'])

    def test_update_time(self):
        """
        tests if the `updated_at` time of a course object is correctly
        updated when the course's field is changed.
        """
        with app.app_context():
            db.session.add(self.course)
            updated_time = datetime.strptime(self.course.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.course.course_credit = "3"
            db.session.commit()
            new_time = datetime.strptime(self.course.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.assertTrue(new_time > updated_time)
