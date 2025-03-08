import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import numpy as np
import pymysql
#import pandas as pd
# استيراد قاعدة البيانات من الملف الجديد
from models import db, User, Course, Enrollment, Student,Grade,Preference
# from flask_mysqldb import MySQL
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import requests	
from db import add_review,get_course_details,get_db_connection,has_reviewed,getchartdata
from recommend import predicted_ratings
from auth import user_login ,user_register#,user_logout
from gpa import getgpauser
#✅ استخدام Random Forest لتوقع أداء الطالب في الدورات القادمة


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
    gpa_data=getgpauser(current_user.id)
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
     user=current_user,gpa=gpa_data)


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


'''
@app.route('/get_courses_api')
def get_courses_api():
  return get_api_coursers()
'''
@app.route('/get_student_data')
def get_student_data():
    data=getchartdata(current_user.id)
    return jsonify(data)
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
       return user_login()

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
     return   user_register()
	
	
	

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
        if user.gpa <= course.gpa_requirement:
            recommendations.append({
                "course_id": course.id,
                "course_name": course.course_name,
                "gpa":course.gpa_requirement,
                "logo": course.logo,
                "reason": "توصية."
            })

    return jsonify({"recommended_courses": recommendations,'gpa':user.gpa})	
	






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
        new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id,rating=0)
        db.session.add(new_enrollment)
        db.session.commit()
        return jsonify({"S":1,"message": "تم الانضمام إلى الدورة بنجاح!"}), 200
    except Exception as e:
        return jsonify({"S":0,"error": str(e)}), 500


@app.route('/gpa')
def gpa():
    return render_template('gpa.html', user=current_user)

@app.route('/close_course/', methods=['GET', 'POST'])
def close_course():
    print("close_course")
    print(request)
    if request.method=='POST':
     grade = request.form['grade']
     id_enr = request.form['id_enr']
     hours = request.form['hours']
     existing_enrollment = Enrollment.query.filter_by(id=id_enr).first()
     if existing_enrollment:
       existing_enrollment.grade=grade
       existing_enrollment.hours=hours
       existing_enrollment.completed=1
       db.session.commit()  # حفظ التغييرات
       return jsonify({"S":1,"message": "تم اقفال الدورة بنجاح"}), 200
    
     else:
       return jsonify({"S":0,"message": "فشل في اقفال الدورة"}), 200

    return render_template('close_course.html', user=current_user,id_enr=request.args.get('id_enr'))
	 



   
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




# صفحة عرض التوصيات
#@app.route('/recommendations')
@app.route('/recommendations/<int:user_id>')
def recommendations(user_id):
       #user_id = current_user.id
       if user_id==0:
        return "الرجاء تسجيل الدخول", 403

        
        if user_id not in predicted_ratings.index:
           return "لا توجد توصيات متاحة لهذا الطالب"

       recommended_courses = predicted_ratings.loc[user_id].sort_values(ascending=False).index.tolist()
    # جلب تفاصيل الدورات من قاعدة البيانات
       conn = get_db_connection()
       cursor = conn.cursor()
       query = "SELECT id, course_name, description,logo FROM courses WHERE id IN (%s)" % ','.join(map(str, recommended_courses[:5]))
       cursor.execute(query)
       courses = cursor.fetchall()
       conn.close()
       return jsonify({"recommended_courses": courses})
       #return render_template('recommendations.html', courses=courses)
'''
@app.route('/recommendations/<int:student_id>')
def get_recommendations(student_id):
    recommended_courses = predicted_ratings.loc[student_id].sort_values(ascending=False).index.tolist()
    return jsonify({"recommended_courses": recommended_courses})

'''

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()
    print("✅ تم إنشاء الجداول في قاعدة البيانات بنجاح!")
print(current_user)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
	#app.run(debug=True)
   
    