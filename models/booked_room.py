#!/usr/bin/env python3


from models.basemodel import BaseModel
from models import db
from sqlalchemy import (
                        String,
                        ForeignKey,
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column
                            )


class Booked(BaseModel, db.Model):
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    room_id: Mapped[str] = mapped_column(String(60), ForeignKey('rooms.id'), nullable=False)
