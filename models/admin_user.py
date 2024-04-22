#!/usr/bin/env python3
from sqlalchemy import String, Table, Column, ForeignKey
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )
from models.basemodel import BaseModel
from models import db, app


admin_roles = Table('admin_roles',
                    BaseModel.metadata,
                    Column('admin_id', String(60), ForeignKey('admins.id')),
                    Column('role_id', String(60), ForeignKey('roles.id')))


class AdminUser(BaseModel, db.Model):
    __tablename__ = 'admins'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    finger_id: Mapped[str] = mapped_column(String(60), nullable=True)
    rf_id: Mapped[str] = mapped_column(String(60), nullable=True)
    roles = relationship('Role', secondary=admin_roles, backref='admins')
