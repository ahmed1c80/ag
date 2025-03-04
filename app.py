import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import numpy as np
# from scipy.sparse.linalg import svds
import pymysql
#import pandas as pd
# استيراد قاعدة البيانات من الملف الجديد
from models import db, User, Course, Enrollment, Student
# from flask_mysqldb import MySQL
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
#from recommendation import get_recommendations
#from sqlalchemy import create_engine
from svd_main import get_recommend
import requests	
from db import add_review,get_course_details,get_db_connection,has_reviewed 
#✅ استخدام Random Forest لتوقع أداء الطالب في الدورات القادمة



import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import joblib  # لحفظ المحول القياسي (Scaler)

import re
app = Flask(__name__)

port = 3306  # تأكد من أنه عدد صحيح

#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://u804311892_agline:Ah#630540@193.203.184.99:3306/u804311892_agline"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:rootroot@localhost:3306/agline"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)  # ربط قاعدة البيانات بتطبيق Flask
bcrypt = Bcrypt(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
#print(type(PORT))  # يجب أن يكون <class 'int'>



@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    conn = get_db_connection()
	
	
	
    cursor = conn.cursor()
    cursor.execute("""
    SELECT courses.*, enrollments.id AS enr_id 
    FROM courses 
    LEFT JOIN enrollments ON courses.id = enrollments.course_id 
    WHERE enrollments.user_id = %s
    """, (user_id,))
    courses = cursor.fetchall()
    cursor.close()	
    return render_template(
    'dashboard.html',
    courses=courses,
    recommendation=[],
    #recommend=svd_main,
     user=current_user)


# تحديث `gpa` للمستخدم
# تحديث GPA للمستخدم
@app.route('/update_gpa', methods=['GET', 'POST'])
def update_gpa():
    if request.method == 'POST':
        try:
            # استقبال البيانات من النموذج أو JSON
            user_id = request.form.get('user_id') or request.json.get('user_id')
            new_gpa = request.form.get('new_gpa') or request.json.get('gpa')

            # البحث عن المستخدم في قاعدة البيانات
            user = User.query.filter_by(id=user_id).first()

            if user:
                user.gpa = float(new_gpa)  # تحديث المعدل التراكمي
                db.session.commit()  # حفظ التغييرات
                flash(f"تم تحديث GPA بنجاح إلى {user.gpa} ✅", "success")
                return redirect(url_for('update_gpa'))
            else:
                flash("المستخدم غير موجود ❌", "danger")

        except Exception as e:
            flash(f"خطأ أثناء تحديث GPA: {str(e)} ❌", "danger")

    # عند زيارة الصفحة بـ GET، يتم عرض النموذج
    return render_template('update_gpa.html', user=current_user)
	
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/get_student_data')
def get_student_data():
    data = {
        "understanding": {
            "labels": ["جبر خطي", "تفاضل وتكامل", "إحصاء", "برمجة"],
            "values": [0, 0, 0, 0]  # نسبة الفهم لكل دورة
        },
        "weakness": {
            "labels": ["تفاضل وتكامل", "إحصاء", "برمجة"],  # المواد التي بها نقاط ضعف
            "values": [0, 0, 0]  # نسبة الضعف في كل مادة
        }
    }
    return jsonify(data)
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = User.query.filter_by(phone=phone).first()
        
        #hashed_password = generate_password_hash(password)
        print(bcrypt.check_password_hash(user.password_hash, password))
        print(password)
		
        if user and bcrypt.check_password_hash(user.password_hash, password):#and check_password_hash(user.password_hash, hashed_password):
            login_user(user)
            return redirect(url_for('dashboard'))
			
            flash('User with this phone already exists!', 'danger')
    return render_template('login.html', title="Login")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/recommend/<int:user_id>')
#@app.route('/recommend')
@login_required
def recommend(user_id):
    recommendations = get_recommend(user_id)#ations(userid)
    print(recommendations.json())
    #return jsonify(recommendations)
    return render_template('recommend.html', title="Recommendations", recommendations=recommendations)




# Validate Phone Number
def is_valid_phone(phone):
    return re.fullmatch(r"^\d{9,15}$", phone) is not None

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        password = request.form['password']
        gpa = request.form.get('gpa', type=float)
        major = request.form['major']

        #if not is_valid_phone(phone):
            #flash('Invalid phone number! Must be 9-15 digits.', 'danger')
            #return redirect(url_for('register'))

        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            flash('User with this phone already exists!', 'danger')
            return redirect(url_for('register'))
        # تشفير كلمة المرور
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #hashed_password = generate_password_hash(password)

        new_user = User(full_name=full_name, phone=phone, password_hash=hashed_password, gpa=gpa, major=major)
        db.session.add(new_user)
        db.session.commit()


        flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
	
	
	

@app.route('/api/recommend_courses/<int:user_id>', methods=['GET'])
def recommend_courses(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    # جلب المقررات التي لم يسجل فيها الطالب
    completed_courses = [e.course_id for e in Enrollment.query.filter_by(user_id=user.id).all()]
    available_courses = Course.query.filter(~Course.id.in_(completed_courses)).all()
    
    recommendations = []
    for course in available_courses:
        # تحليل البيانات ومعايير التوصية
        if user.gpa >= course.gpa_requirement:
            recommendations.append({
                "course_id": course.id,
                "course_name": course.course_name,
                "logo": course.logo,
                "reason": "Recommended based on GPA and previous courses."
            })

    return jsonify({"recommended_courses": recommendations,'gpa':user.gpa})	

# ✅ API لاسترجاع الدورات الموصى بها بناءً على المعدل التراكمي
@app.route('/api/recommend_coursesp', methods=['GET'])
def recommend_coursesp():
    if current_user.id==0:
        return jsonify({"error": "User not logged in"}), 401

    student_id = current_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 استرجاع معدل الطالب التراكمي
    cursor.execute("SELECT gpa FROM users WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    student_gpa = student['gpa']

    # 🔹 استرجاع الدورات المناسبة بناءً على المعدل التراكمي
    cursor.execute("""
        SELECT *
        FROM courses
        WHERE gpa_requirement <= %s
        ORDER BY gpa_requirement DESC
    """, (student_gpa,))

    recommendations = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(recommendations)
	
	
# ✅ API لجلب الدورات من Udemy أو Coursera
@app.route('/api/web_courses', methods=['GET'])
def get_web_courses():
    query = request.args.get("query", "Linear Algebra")
    
    # 🔹 استعلام Udemy API
    udemy_url = "https://www.udemy.com/api-2.0/courses/"
    udemy_params = {"search": query, "page_size": 5}
    udemy_headers = {"Authorization": "Bearer YOUR_UDEMY_API_KEY"}

    udemy_response = requests.get(udemy_url, params=udemy_params, headers=udemy_headers)
    udemy_courses = udemy_response.json().get("results", []) if udemy_response.status_code == 200 else []

    # 🔹 تجميع النتائج
    recommendations = [{"title": c["title"], "url": c["url"], "platform": "Udemy"} for c in udemy_courses]

    return jsonify(recommendations)








@app.route('/join_course', methods=['POST'])
@login_required  # يتطلب تسجيل الدخول
def join_course():
    try:
        data = request.get_json()  # استقبال البيانات من AJAX
        course_id = data.get("course_id")

        # التحقق من صحة البيانات
        if not course_id:
            return jsonify({"S":0,"error": "Course ID is required"}), 400

        # التحقق من وجود الدورة
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"S":0,"error": "الدورة غير موجودة"}), 404

        # التحقق مما إذا كان الطالب مسجلاً مسبقًا
        existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if existing_enrollment:
            return jsonify({"S":0,"error": "لقد قمت بالتسجيل بالفعل في هذه الدورة"}), 400

        # تسجيل الطالب في الدورة
        new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()

        return jsonify({"S":1,"message": "تم الانضمام إلى الدورة بنجاح!"}), 200

    except Exception as e:
        return jsonify({"S":0,"error": str(e)}), 500


# تحميل النموذج المدرب
#model = keras.models.load_model("gpa_predictor.h5")
# تحميل النموذج مع تمرير دالة MSE كـ custom object
model = keras.models.load_model("gpa_predictor.h5", custom_objects={"mse": keras.losses.MeanSquaredError()})
# تحميل المحول القياسي (Scaler) المستخدم أثناء التدريب
scaler = joblib.load("scaler.pkl")

@app.route('/gpa')
def gpa():

    return render_template('gpa.html', user=current_user)

# API لتوقع المعدل التراكمي
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        user_id = current_user.id
        features = np.array(data['features']).reshape(1, -1)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0][0].clip(0, 5)

        # حفظ البيانات في قاعدة البيانات
        new_student = Student(
            user_id=user_id,
            study_hours=features[0][0],
            previous_gpa=features[0][1],
            difficulty_level=features[0][2],
            attendance_rate=features[0][3],
            major=features[0][4],
            predicted_gpa=round(float(prediction), 2)
        )
        db.session.add(new_student)
        db.session.commit()

        return jsonify({'predicted_gpa': round(float(prediction), 2)})

    except Exception as e:
        return jsonify({'error': str(e)})

# API لاسترجاع جميع التوقعات
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    students_data = [
        {
            'id': student.id,
            'user_id': student.user_id,
            'study_hours': student.study_hours,
            'previous_gpa': student.previous_gpa,
            'difficulty_level': student.difficulty_level,
            'attendance_rate': student.attendance_rate,
            'major': student.major,
            'predicted_gpa': float(student.predicted_gpa)
        }
        for student in students
    ]
    return jsonify(students_data)



   
@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_profile(course_id):
    if current_user.id==0:
        flash("⚠️ يجب تسجيل الدخول لتقييم الدورات!", "warning")
        return redirect(url_for('login'))

    #student_id=current_user.id
    already_reviewed = has_reviewed(course_id, current_user.id)  # فحص التقييم المسبق
    if request.method == 'POST':
        rating = int(request.form['rating'])
        
        if add_review(course_id,rating):
            flash("✅ تم إضافة التقييم بنجاح!", "success")
        else:
            flash("⚠️ لقد قمت بالفعل بتقييم هذه الدورة!", "danger")
        
        return redirect(url_for('course_profile', course_id=course_id))

    course, reviews = get_course_details(course_id)
    return render_template('course_profile.html', course=course, reviews=reviews, user=current_user, already_reviewed=already_reviewed)

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()
    print("✅ تم إنشاء الجداول في قاعدة البيانات بنجاح!")
print(current_user)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
	#app.run(debug=True)
   
    