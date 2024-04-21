#!/usr/bin/env python3

from models.room import Room
from models import db, app
from datetime import datetime
import unittest


class TestRoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = {
            'block_no': 'B57',
            'room_no': '2007',
        }
        cls.room = Room(**cls.data)
        with app.app_context():
            db.session.add(cls.room)
            db.session.commit()


    @classmethod
    def tearDownClass(cls) -> None:
        # time.sleep(10)
        with app.app_context():
            db.session.delete(cls.room)
            db.session.commit()

    def test_room_data(self):
        """
        adds a room to the database and asserts the presence of
        specific attributes for the room.
        """
        with app.app_context():
            db.session.add(self.room)

            self.assertTrue(getattr(self.room, 'block_no'))
            self.assertEqual(self.room.block_no, self.data['block_no'])

            self.assertTrue(getattr(self.room, 'room_no'))
            self.assertEqual(self.room.room_no, self.data['room_no'])

    def test_update_time(self):
        """
        tests if the `updated_at` time of a room object is correctly
        updated when the room's field is changed.
        """
        with app.app_context():
            db.session.add(self.room)
            updated_time = datetime.strptime(self.room.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.room.block_no = "B34"
            db.session.commit()
            new_time = datetime.strptime(self.room.updated_at, "%Y-%m-%d %H:%M:%S.%f")
            self.assertTrue(new_time > updated_time)
