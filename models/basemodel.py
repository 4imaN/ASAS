
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from sqlalchemy import String
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv
from os import getenv
from sqlalchemy.orm import (
                            DeclarativeBase,
                            Mapped,
                            mapped_column
                            )


load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
admin = Admin(app, name="Admin Only")


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(String(60), default=lambda: str(uuid4()), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(String(60), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(String(60), default=datetime.now, onupdate=datetime.now)

    def get_id(self):
        return self.id


db = SQLAlchemy(model_class=BaseModel)
db.init_app(app)


class Role(BaseModel, db.Model):
    __tablename__ = 'roles'
    name: Mapped[str] = mapped_column(String(60), unique=True)
    description: Mapped[str] = mapped_column(String(255))