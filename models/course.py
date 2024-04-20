#!/usr/bin/env python3


from models.basemodel import BaseModel
from models import db
from models.assigned_students import AssignedStudent
from sqlalchemy import String
from typing import List
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )

# student_course = Table('student_course', BaseModel.metadata,
#                        Column('student_id', ForeignKey('students.id'), primary_key=True),
#                        Column('course_id', ForeignKey('courses.id'), primary_key=True)
#                        )


class Course(BaseModel, db.Model):
    __tablename__ = 'courses'
    course_code: Mapped[str] = mapped_column(String(60), nullable=False)
    course_name: Mapped[str] = mapped_column(String(60), nullable=False)
    course_credit: Mapped[str] = mapped_column(String(60), nullable=False)
    course_category: Mapped[str] = mapped_column(String(60), default='Common', nullable=False)
    assigned_students: Mapped[List['AssignedStudent']] = relationship('AssignedStudent', back_populates='course', cascade='all')
