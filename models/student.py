#!/usr/bin/env python3
from sqlalchemy import String, Integer
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column
                            )
from models.basemodel import BaseModel
from models import db


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
    department: Mapped[str] = mapped_column(String(100))
    finger_id: Mapped[str] = mapped_column(String(60))
    rf_id: Mapped[str] = mapped_column(String(60))
    batch_section: Mapped[str] = mapped_column(String(60))
