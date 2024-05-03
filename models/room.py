


from models.basemodel import BaseModel
from models import db
from models.booked_room import Booked
from typing import List
from sqlalchemy import (
                        String,
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )


class Room(BaseModel, db.Model):
    __tablename__ = 'rooms'
    block_no: Mapped[str] = mapped_column(String(10), nullable=False)
    room_no: Mapped[str] = mapped_column(String(10), nullable=False)
    booked_rooms: Mapped[List['Booked']] = relationship('Booked', back_populates='room')
