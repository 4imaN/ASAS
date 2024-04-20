#!/usr/bin/env python3


from models.basemodel import BaseModel
from models import db
from sqlalchemy import (
                        String,
                        Integer,
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column
                            )


class Room(BaseModel, db.Model):
    __tablename__ = 'rooms'
    block_no: Mapped[int] = mapped_column(Integer, nullable=False)
    room_no: Mapped[str] = mapped_column(String(60), nullable=False)
