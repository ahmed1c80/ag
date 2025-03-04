from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
db = SQLAlchemy()  # إنشاء كائن قاعدة البيانات



# نموذج المستخدم

class User(UserMixin, db.Model):
 id = db.Column(db.Integer, primary_key=True)
 username = db.Column(db.String(150), unique=True, nullable=False)
 password = db.Column(db.String(150), nullable=False)
 gpa = db.Column(db.Float, nullable=False)

class Student(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 gpa = db.Column(db.Float, nullable=False)
 major = db.Column(db.String(255), nullable=False)
 interests = db.Column(db.Text, nullable=False)

# نموذج الدورة التدريبية
class Course(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 #student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 course_name = db.Column(db.String(255), nullable=False)
 completion_date = db.Column(db.Date, nullable=False)
 grade = db.Column(db.String(10), nullable=True)

# نموذج تسجيل الطالب في الدورات
class Enrollment(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
 course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
 rating = db.Column(db.Float, nullable=False)



import sqlite3

# الاتصال بقاعدة البيانات (سيتم إنشاؤها إن لم تكن موجودة)
#db = sqlite3.connect("example.db")