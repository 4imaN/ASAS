


from models.basemodel import BaseModel
from models import db
from sqlalchemy import (
                        String,
                        ForeignKey,
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )


class Booked(BaseModel, db.Model):
    __tablename__ = 'booked_rooms'
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    room_id: Mapped[str] = mapped_column(String(60), ForeignKey('rooms.id'), nullable=False)
    instructor = relationship('Instructor', back_populates='booked_rooms')
    room = relationship('Room', back_populates='booked_rooms')
