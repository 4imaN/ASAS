
from sqlalchemy import String, Column, ForeignKey, Table, DateTime, Integer
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
from flask_security import UserMixin


instructor_roles = Table('instructor_roles',
                    BaseModel.metadata,
                    Column('instructor_id', String(60), ForeignKey('instructors.id')),
                    Column('role_id', String(60), ForeignKey('roles.id')))



class Instructor(db.Model, UserMixin):
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
    roles = relationship('Role', secondary=instructor_roles, backref='instructors')


   # setups for flask-security
    active: Mapped[str] = mapped_column(String(60), nullable=True)
    def is_active(self):
        return super().is_active
    # is_active = mapped_column(String(60), default=True, nullable=False)
    current_login_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    current_login_ip: Mapped[str] = mapped_column(String(60), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=True)
    confirmed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    def is_authenticated(self):
        return super().is_authenticated()


