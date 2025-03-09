from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  # إنشاء كائن قاعدة البيانات

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
    hours = db.Column(Integer, default=0)
    enrollment_date = db.Column(TIMESTAMP, default=datetime.utcnow)
    completed  = db.Column(Integer, default=0)
    rating = db.Column(Integer, default=0)  # Rating from 0.0 to 5.0
    grade = db.Column(db.String(2), nullable=True)  # A, B, C, D, F
    attempts = db.Column(db.Integer, nullable=False, default=1)


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
	
	
	
	
# جدول الدرجات
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.String(2), nullable=False)  # A, B, C, D, F
    attempts = db.Column(db.Integer, nullable=False, default=1)

# جدول اهتمامات الطالب
class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_style = db.Column(db.String(100), nullable=True)  # بصري، سمعي، عملي
    interests = db.Column(db.Text, nullable=True)
    


# تعريف نموذج Courses
class CoursesEdx(db.Model):
    __tablename__ = 'coursers_edx'
    id = db.Column(db.Integer, primary_key=True)  # معرف فريد
    course_id = db.Column(db.String(255), unique=True, nullable=False)  # معرف الدورة (فريد)
    blocks_url = db.Column(db.Text)  # رابط الكتل
    effort = db.Column(db.String(50))  # الجهد المطلوب
    enrollment_start = db.Column(db.DateTime)  # تاريخ بدء التسجيل
    enrollment_end = db.Column(db.DateTime)  # تاريخ انتهاء التسجيل
    name = db.Column(db.String(255), nullable=False)  # اسم الدورة
    number = db.Column(db.String(100))  # رقم الدورة
    org = db.Column(db.String(100))  # المنظمة
    short_description = db.Column(db.Text)  # وصف مختصر
    start = db.Column(db.DateTime)  # تاريخ البدء
    start_display = db.Column(db.String(100))  # تاريخ البدء (عرض نصي)
    start_type = db.Column(db.String(50))  # نوع تاريخ البدء
    pacing = db.Column(db.String(50))  # وتيرة الدورة
    mobile_available = db.Column(db.Boolean, default=False)  # هل الدورة متاحة على المحمول؟
    hidden = db.Column(db.Boolean, default=False)  # هل الدورة مخفية؟
    invitation_only = db.Column(db.Boolean, default=False)  # هل الدورة متاحة فقط عن طريق الدعوة؟
    banner_image_url = db.Column(db.Text)  # رابط صورة البانر
    course_image_url = db.Column(db.Text)  # رابط صورة الدورة
    course_video_url = db.Column(db.Text)  # رابط فيديو الدورة

'''
    def __repr__(self):
        return f"<Course {self.name}>"

# إنشاء الجداول في قاعدة البيانات (يتم تنفيذها مرة واحدة)
with app.app_context():
    db.create_all()

# دالة لإدراج أو تحديث دورة
def insert_or_update_course(course_data):
    # البحث عن الدورة باستخدام course_id
    course = Courses.query.filter_by(course_id=course_data.get('id')).first()

    if course:
        # تحديث البيانات إذا كانت الدورة موجودة
        course.blocks_url = course_data.get('blocks_url')
        course.effort = course_data.get('effort')
        course.enrollment_start = course_data.get('enrollment_start')
        course.enrollment_end = course_data.get('enrollment_end')
        course.name = course_data.get('name')
        course.number = course_data.get('number')
        course.org = course_data.get('org')
        course.short_description = course_data.get('short_description')
        course.start = course_data.get('start')
        course.start_display = course_data.get('start_display')
        course.start_type = course_data.get('start_type')
        course.pacing = course_data.get('pacing')
        course.mobile_available = course_data.get('mobile_available', False)
        course.hidden = course_data.get('hidden', False)
        course.invitation_only = course_data.get('invitation_only', False)
        course.banner_image_url = course_data.get('media', {}).get('banner_image', {}).get('uri_absolute')
        course.course_image_url = course_data.get('media', {}).get('course_image', {}).get('uri')
        course.course_video_url = course_data.get('media', {}).get('course_video', {}).get('uri')
        print(f"تم تحديث الدورة: {course.name}")
    else:
        # إدراج دورة جديدة إذا لم تكن موجودة
        new_course = Courses(
            course_id=course_data.get('id'),
            blocks_url=course_data.get('blocks_url'),
            effort=course_data.get('effort'),
            enrollment_start=course_data.get('enrollment_start'),
            enrollment_end=course_data.get('enrollment_end'),
            name=course_data.get('name'),
            number=course_data.get('number'),
            org=course_data.get('org'),
            short_description=course_data.get('short_description'),
            start=course_data.get('start'),
            start_display=course_data.get('start_display'),
            start_type=course_data.get('start_type'),
            pacing=course_data.get('pacing'),
            mobile_available=course_data.get('mobile_available', False),
            hidden=course_data.get('hidden', False),
            invitation_only=course_data.get('invitation_only', False),
            banner_image_url=course_data.get('media', {}).get('banner_image', {}).get('uri_absolute'),
            course_image_url=course_data.get('media', {}).get('course_image', {}).get('uri'),
            course_video_url=course_data.get('media', {}).get('course_video', {}).get('uri')
        )
        db.session.add(new_course)
        print(f"تم إدراج الدورة: {new_course.name}")

    # حفظ التغييرات في قاعدة البيانات
    db.session.commit()

# مثال لبيانات JSON
course_json = {
    'blocks_url': 'https://courses.edx.org/api/courses/v2/blocks/?course_id=ccx-v1%3Aadam%2BMac_APccx%2Be0d%2Bccx%403',
    'effort': '2:00',
    'end': None,
    'enrollment_start': '2015-07-21T10:00:00Z',
    'enrollment_end': '2016-06-29T10:00:00Z',
    'id': 'ccx-v1:adam+Mac_APccx+e0d+ccx@3',
    'media': {
        'banner_image': {'uri': '/asset-v1:adam+Mac_APccx+e0d+type@asset+block@images_course_image.jpg', 'uri_absolute': 'https://courses.edx.org/asset-v1:adam+Mac_APccx+e0d+type@asset+block@images_course_image.jpg'},
        'course_image': {'uri': '/asset-v1:adam+Mac_APccx+e0d+type@asset+block@Davidson_EdX-68_1_.png'},
        'course_video': {'uri': 'http://www.youtube.com/watch?v=sAnHwOL8aAs'},
        'image': {'raw': 'https://courses.edx.org/asset-v1:adam+Mac_APccx+e0d+type@asset+block@Davidson_EdX-68_1_.png', 'small': 'https://courses.edx.org/asset-v1:adam+Mac_APccx+e0d+type@thumbnail+block@Davidson_EdX-68_1_-png-375x200.jpg', 'large': 'https://courses.edx.org/asset-v1:adam+Mac_APccx+e0d+type@thumbnail+block@Davidson_EdX-68_1_-png-750x400.jpg'}
    },
    'name': 'ntest',
    'number': 'Mac_APccx',
    'org': 'adam',
    'short_description': '',
    'start': '2016-06-27T14:10:44Z',
    'start_display': 'June 27, 2016',
    'start_type': 'timestamp',
    'pacing': 'instructor',
    'mobile_available': False,
    'hidden': False,
    'invitation_only': False,
    'course_id': 'ccx-v1:adam+Mac_APccx+e0d+ccx@3'
}
'''