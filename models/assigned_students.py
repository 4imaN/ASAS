
from models.basemodel import BaseModel
from models import db
from datetime import datetime
from sqlalchemy import (
                        String,
                        ForeignKey,
                        DateTime,
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )


class AssignedStudent(BaseModel, db.Model):
    __tablename__ = 'assigned_students'

    student_id: Mapped[str] = mapped_column(String(60), ForeignKey('students.id'), nullable=False)
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    course_id: Mapped[str] = mapped_column(String(60), ForeignKey('courses.id'), nullable=False)
    student = relationship('Student', back_populates='assigned_students')
    instructor = relationship('Instructor', back_populates='assigned_students')
    course = relationship('Course', back_populates='assigned_students')

    year: Mapped[DateTime] = mapped_column(String(60), default=datetime.utcnow, nullable=False)
    semister: Mapped[str] = mapped_column(String(10), nullable=False)
    batch: Mapped[str] = mapped_column(String(10), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)