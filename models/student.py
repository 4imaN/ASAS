
from sqlalchemy import String, Boolean
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )
from models.basemodel import BaseModel
from models import db, admin
from models.assigned_students import AssignedStudent
from models.student_attendance import StuAttendance
from typing import List


class Student(BaseModel, db.Model):
    __tablename__ = 'students'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    registered: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=True)
    student_id: Mapped[str] = mapped_column(String(60), unique=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    finger_id: Mapped[str] = mapped_column(String(60), nullable=True)
    rf_id: Mapped[str] = mapped_column(String(60), nullable=True)
    add: Mapped[Boolean] = mapped_column(Boolean, default=False, nullable=False)
    batch_section: Mapped[str] = mapped_column(String(60), nullable=False)
    assigned_students: Mapped[List['AssignedStudent']] = relationship('AssignedStudent', back_populates='student')
    student_attendance: Mapped[List['StuAttendance']] = relationship(back_populates='student')
