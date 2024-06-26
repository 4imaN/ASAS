


from models.basemodel import BaseModel
from models import db
from datetime import datetime, timedelta
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


class StuAttendance(BaseModel, db.Model):
    __tablename__ = 'student_attendance'
    session_id: Mapped[str] = mapped_column(String(60), ForeignKey('sessions.id'), nullable=False)
    course_id: Mapped[str] = mapped_column(String(60), ForeignKey('courses.id'), nullable=False)
    student_id: Mapped[str] = mapped_column(String(60), ForeignKey('students.id'), nullable=False)
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    room_id: Mapped[str] = mapped_column(String(60), ForeignKey('rooms.id'), nullable=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, default=(datetime.now() + timedelta(minutes=15)))
    arrived_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    student = relationship('Student', back_populates='student_attendance')
    session = relationship('InstAttendance', back_populates='student_attendance')