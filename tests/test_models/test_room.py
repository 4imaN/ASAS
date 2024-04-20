#!/usr/bin/env python3

from models.room import Room
from models import db, app
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
