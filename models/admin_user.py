
from sqlalchemy import String, Table, \
    Column, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )
from models.basemodel import BaseModel
from models import db, app
from flask_security import UserMixin


admin_roles = Table('admin_roles',
                    BaseModel.metadata,
                    Column('admin_id', String(60), ForeignKey('admins.id')),
                    Column('role_id', String(60), ForeignKey('roles.id')))


class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admins'
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    new: Mapped[Boolean] = mapped_column(Boolean, default=True, nullable=False)
    finger_id: Mapped[str] = mapped_column(String(60), nullable=True)
    rf_id: Mapped[str] = mapped_column(String(60), nullable=True)
    roles = relationship('Role', secondary=admin_roles, backref='admins')

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
