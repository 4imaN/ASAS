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
from typing import List


class Instructor(BaseModel, db.Model):
    __tablename__ = 'instructors'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    teacher_id: Mapped[str] = mapped_column(String(60), unique=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    department: Mapped[str] = mapped_column(String(100))
    finger_id: Mapped[str] = mapped_column(String(60))
    rf_id: Mapped[str] = mapped_column(String(60))
    qualification: Mapped[str] = mapped_column(String(60), nullable=False)
    students: Mapped[List['AssignedStudent']] = relationship(back_populates='instructor')
