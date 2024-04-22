#!/usr/bin/env python3
from sqlalchemy import String
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )
from models.basemodel import BaseModel
from models import db, admin
from models.instructor_session import InstAttendance
from models.assigned_students import AssignedStudent
from models.booked_room import Booked
from typing import List


class Instructor(BaseModel, db.Model):
    __tablename__ = 'instructors'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    teacher_id: Mapped[str] = mapped_column(String(60), unique=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    finger_id: Mapped[str] = mapped_column(String(60), nullable=True)
    rf_id: Mapped[str] = mapped_column(String(60), nullable=True)
    qualification: Mapped[str] = mapped_column(String(60), nullable=False)
    assigned_students: Mapped[List['AssignedStudent']] = relationship('AssignedStudent', back_populates='instructor')
    sessions: Mapped[List['InstAttendance']] = relationship('InstAttendance', back_populates='instructor', cascade='all')
    booked_rooms: Mapped[List['Booked']] = relationship('Booked', back_populates='instructor', cascade='all')
