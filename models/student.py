#!/usr/bin/env python3
from sqlalchemy import String
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )
from models.basemodel import BaseModel
from models import db
from models.assigned_students import AssignedStudent
from models.student_attendance import StuAttendance
from typing import List


class Student(BaseModel, db.Model):
    __tablename__ = 'students'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    registered: Mapped[bool] = mapped_column(nullable=False, default=True)
    student_id: Mapped[str] = mapped_column(String(60), unique=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    finger_id: Mapped[str] = mapped_column(String(60), nullable=True)
    rf_id: Mapped[str] = mapped_column(String(60), nullable=True)
    batch_section: Mapped[str] = mapped_column(String(60), nullable=False)
    assigned_students: Mapped[List['AssignedStudent']] = relationship('AssignedStudent', back_populates='student', cascade='all')
    student_attendance: Mapped[List['StuAttendance']] = relationship(back_populates='student')
