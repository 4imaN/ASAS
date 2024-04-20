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


class Course(BaseModel, db.Model):
    __tablename__ = 'courses'
    course_code: Mapped[str] = mapped_column(String(60), nullable=False)
    course_name: Mapped[str] = mapped_column(String(60), nullable=False)
    course_credit: Mapped[str] = mapped_column(String(60), nullable=False)
    course_category: Mapped[str] = mapped_column(String(60), default='Common', nullable=False)
    assigns: Mapped[List['AssignedStudent']] = relationship(back_populates='course', cascade='all')
