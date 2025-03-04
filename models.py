from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  # إنشاء كائن قاعدة البيانات

# Database Connection
DATABASE_URL = "mysql+pymysql://root:rootroot@localhost/agline"
engine = create_engine(DATABASE_URL, echo=True)
#db = SQLAlchemy()  # إنشاء كائن قاعدة البيانات

#Base = declarative_base()

# Users Table (Updated: Replaced email with phone)
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(String(255), nullable=False)
    phone = db.Column(String(15), unique=True, nullable=False)  # Updated field
    password_hash = db.Column(String(255), nullable=False)
    gpa = db.Column(DECIMAL(3, 2), nullable=True)
    major = db.Column(String(255), nullable=True)
    created_at = db.Column(TIMESTAMP, default=datetime.utcnow)

    #enrollments = relationship("Enrollment", back_populates="user")

# Courses Table
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(String(255), nullable=False)
    logo = db.Column(String(255), nullable=True)
    course_code = db.Column(String(50), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    instructor = db.Column(String(255), nullable=True)
    credits = db.Column(Integer, nullable=False)
    university = db.Column(String(255), nullable=True)
    difficulty_level = db.Column(Enum('Beginner', 'Intermediate', 'Advanced'), nullable=False)
    prerequisites = db.Column(Text, nullable=True)
    gpa_requirement = db.Column(DECIMAL(3, 2), nullable=True)
    language = db.Column(Enum('English', 'Arabic', 'Other'), nullable=False, default='English')
    created_at = db.Column(TIMESTAMP, default=datetime.utcnow)

    #enrollments = relationship("Enrollment", back_populates="course")

# Enrollments Table (User-Course Relationship)
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    course_id = db.Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))
    enrollment_date = db.Column(TIMESTAMP, default=datetime.utcnow)
    completed  = db.Column(Integer, default=0)
    rating = db.Column(DECIMAL(2, 1), nullable=True)  # Rating from 0.0 to 5.0

    #user = relationship("User", back_populates="enrollments")
    #course = relationship("Course", back_populates="enrollments")


# تعريف جدول الطلاب في SQLAlchemy
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    study_hours = db.Column(db.Float)
    previous_gpa = db.Column(db.Float)
    difficulty_level = db.Column(db.Float)
    attendance_rate = db.Column(db.Float)
    major = db.Column(db.Float)
    predicted_gpa = db.Column(db.Float)
# Create Tables
#Base.metadata.create_all(engine)

# Create a session
#Session = sessionmaker(bind=engine)
#session = Session()
'''
# Example: Add a new user with phone number
def add_user(name, phone, password_hash, gpa, major):
    user = User(
        full_name=name,
        phone=phone,
        password_hash=password_hash,
        gpa=gpa,
        major=major
    )
    #session.add(user)
    #session.commit()
    print(f"User {name} added with phone {phone}.")
'''
# Example Usage
# add_user("Alice Doe", "1234567890", "hashed_password", 3.8, "Mathematics")