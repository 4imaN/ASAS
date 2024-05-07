


from models.basemodel import BaseModel
from models.student_attendance import StuAttendance
from models import db
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import (
                        String,
                        Integer,
                        ForeignKey,
                        DateTime
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )


class InstAttendance(BaseModel, db.Model):
    __tablename__ = 'sessions'
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    course_id: Mapped[str] = mapped_column(String(60), ForeignKey('courses.id'))
    room_id: Mapped[str] = mapped_column(String(60), ForeignKey('rooms.id'), nullable=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=(datetime.now() + timedelta(minutes=15)))
    end_time: Mapped[str] = mapped_column(String(60), nullable=True)

    student_attendance: Mapped[List['StuAttendance']] = relationship(back_populates='session', cascade='all')
    verfied: Mapped[bool] = mapped_column(default=False)
    instructor = relationship('Instructor', back_populates='sessions')