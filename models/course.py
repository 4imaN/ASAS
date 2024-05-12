


from models.basemodel import BaseModel
from models import db
from models.assigned_students import assign_courses
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
                            Mapped,
                            mapped_column,
                            relationship
                            )

# student_course = Table('student_course', BaseModel.metadata,
#                        Column('student_id', ForeignKey('students.id'), primary_key=True),
#                        Column('course_id', ForeignKey('courses.id'), primary_key=True)
#                        )


class Course(BaseModel, db.Model):
    __tablename__ = 'courses'
    course_code: Mapped[str] = mapped_column(String(60), unique=True)
    course_name: Mapped[str] = mapped_column(String(60), nullable=False)
    course_credit: Mapped[str] = mapped_column(String(60), nullable=False)
    course_category: Mapped[str] = mapped_column(String(60), default='Common', nullable=False)
    course_department: Mapped[str] = mapped_column(String(60), nullable=False)
    # instructor_id: Mapped[str] = mapped_column(String(60), ForeignKey('instructors.id'), nullable=False)

    # course_outline path
