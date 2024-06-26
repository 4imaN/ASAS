
from models.basemodel import BaseModel
from models import db
from datetime import datetime
from typing import List
from models.instructor_session import InstAttendance
from models.student_attendance import StuAttendance
from sqlalchemy import (
                        String,
                        ForeignKey,
                        DateTime,
                        Table,
                        Column,
                        UniqueConstraint
                       )
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )


assign_students = Table('assigned_students',
                        BaseModel.metadata,
                        Column('student_id', String(60), ForeignKey('students.id')),
                        Column('assign_id', String(60), ForeignKey('assignations.id')),
                        UniqueConstraint('student_id', 'assign_id', name='unqiue_student_assign'))

assign_instructors = Table('assigned_instructors',
                           BaseModel.metadata,
                           Column('instructor_id', String(60), ForeignKey('instructors.id')),
                           Column('assign_id', String(60), ForeignKey('assignations.id')),
                           Column('course_id', String(60), ForeignKey('courses.id')),
                        #    UniqueConstraint('instructor_id', 'assign_id', 'course_id', name='unqiue_instructor_assign')
                        )

assign_courses = Table('assigned_courses',
                       BaseModel.metadata,
                       Column('assign_id', String(60), ForeignKey('assignations.id')),
                       Column('course_id', String(60), ForeignKey('courses.id')),
                       UniqueConstraint('course_id', 'assign_id', name='unqiue_course_assign'))

class AssignedStudent(BaseModel, db.Model):
    __tablename__ = 'assignations'

    year: Mapped[DateTime] = mapped_column(String(60), default=(datetime.now()).year, nullable=False)
    department: Mapped[str] = mapped_column(String(60), nullable=False)
    semister: Mapped[str] = mapped_column(String(10), nullable=False)
    batch: Mapped[str] = mapped_column(String(10), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)

    students = relationship('Student', secondary=assign_students, backref='students')
    instructors = relationship('Instructor', secondary=assign_instructors, backref='instructors')
    courses = relationship('Course', secondary=assign_courses, backref='courses')
