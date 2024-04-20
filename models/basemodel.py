#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import (
                            DeclarativeBase,
                            Mapped,
                            mapped_column
                            )


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(String(60), default=lambda: str(uuid4()), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(String(60), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(String(60), default=datetime.now, onupdate=datetime.now)


db = SQLAlchemy(BaseModel)
db.init_app(app)
