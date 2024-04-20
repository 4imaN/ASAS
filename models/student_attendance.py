#!/usr/bin/env python3


from models.basemodel import BaseModel
from models import db
from datetime import datetime
from sqlalchemy import (
                        String,
                        Integer,
                        ForeignKey,
                        DateTime
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column
                            )


class StuAttendance(BaseModel, db.Model):
    session_id: Mapped[str] = mapped_column(String(60), ForeignKey('sessions.id'), nullable=False)
    student_id: Mapped[str] = mapped_column(String(60), ForeignKey('students.id'), nullable=False)
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    room_id: Mapped[str] = mapped_column(String(60), ForeignKey('rooms.id'), nullable=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[DateTime] = mapped_column(DateTime)