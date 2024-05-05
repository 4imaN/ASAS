
from sqlalchemy import String, Boolean, DateTime, Integer, \
    Table, Column, ForeignKey
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

student_roles = Table('student_roles',
                     BaseModel.metadata,
                     Column('role_id', String(60), ForeignKey('roles.id')),
                     Column('student_id', String(60), ForeignKey('students.id')))


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
    roles = relationship('Role', secondary=student_roles, backref='students')

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
