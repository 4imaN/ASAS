#!/usr/bin/env python3


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


class AssignedStudent(BaseModel, db.Model):
    __tablename__ = 'assigned_students'

    student_id: Mapped[str] = mapped_column(String(60), ForeignKey('students.id'), nullable=False)
    instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)
    course_id: Mapped[str] = mapped_column(String(60), ForeignKey('courses.id'), nullable=False)
    student = relationship('Student', back_populates='assigned_students')
    instructor = relationship('Instructor', back_populates='assigned_students')
    course = relationship('Course', back_populates='assigned_students')