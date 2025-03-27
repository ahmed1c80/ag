import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Course, Enrollment, CoursesEdx
from db import add_review, get_course_details, get_db_connection, has_reviewed, getchartdata
from recommend import predicted_ratings, load_recommendation, getcoursersStudent,get_course_recommendations
from auth import user_login, user_register
from gpa import getgpauser

import re
import pymysql

app = Flask(__name__)

# إعدادات قاعدة البيانات

#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://u804311892_agline:Ah#630540@193.203.184.99:3306/u804311892_agline"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:rootroot@localhost:3306/agline"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# تهيئة مكتبات Flask
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# تحميل بيانات المستخدم عند تسجيل الدخول
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========================== 1️⃣ الصفحة الرئيسية (لوحة التحكم) ==========================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """عرض لوحة التحكم للمستخدم بعد تسجيل الدخول"""
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    
    # التحقق من تحديث المعدل التراكمي
    if not user.gpa:
        user.gpa = 1.0
        db.session.commit()

    # جلب بيانات المستخدم والدورات
    courses = getcoursersStudent(user_id)
    gpa_data = getgpauser(user_id)

    return render_template('dashboard.html', courses=courses, recommendation=[], coursesex=[], user=current_user, gpa=gpa_data)



@app.route('/get_student_data')
@login_required
def get_student_data():
    data=getchartdata(current_user.id)
    return jsonify(data)


# ========================== 2️⃣ تحديث بيانات المستخدم (GPA والتخصص) ==========================
@app.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    """تحديث بيانات المستخدم مثل المعدل التراكمي والتخصص"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_id =data.get('user_id')# request.form.get('user_id') or request.json.get('user_id')
            new_gpa =data.get('new_gpa')# request.form.get('new_gpa') or request.json.get('gpa')
            new_major =data.get('new_major')# request.form.get('new_major') or request.json.get('major')

            user = User.query.filter_by(id=user_id).first()
            if user:
                user.gpa =float(new_gpa)# float(f"{new_gpa}")
                user.major = new_major
                db.session.commit()
                return jsonify({"S":1,"message": "تم تحديث الحساب بنجاح"}), 200
                #flash(f"تم تحديث بياناتك بنجاح! ✅", "success")
                #return redirect(url_for('update_user'))
            else:
                return jsonify({"S":0,"message": "المستخدم غير موجود ❌"}), 200
                #flash("المستخدم غير موجود ❌", "danger")
        except Exception as e:
                return jsonify({"S":0,"message": f"خطأ أثناء التحديث: {str(e)} ❌"}), 200
            #flash(f"خطأ أثناء التحديث: {str(e)} ❌", "danger")

    user = User.query.filter_by(id=request.args.get('user_id')).first()
    return render_template('update_gpa.html', user=user)

# ========================== 3️⃣ تسجيل الدخول والخروج ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    return user_login()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    return user_register()

# ========================== 4️⃣ عرض التوصيات للمستخدم ==========================
@app.route('/recommend/<int:user_id>')
@login_required
def recommend(user_id):
    """جلب التوصيات للطالب بناءً على مستواه الأكاديمي واهتماماته"""
    recommended_course_ids, recommended_similarity = load_recommendation(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # استبعاد الدورات التي سجل فيها المستخدم
    query = f"""
        SELECT id, course_name, description, logo, difficulty_level, gpa_requirement ,course_url
        FROM courses 
        WHERE id IN ({','.join(['%s'] * len(recommended_course_ids))})
    """
    cursor.execute(query, recommended_course_ids)
    recommended_courses = cursor.fetchall()
    
    # إضافة نسبة التشابه لكل دورة
    for idx, course in enumerate(recommended_courses):
        course['sim'] = f"{recommended_similarity[idx]:.2f}"

    cursor.close()
    conn.close()
    return jsonify({"recommended_courses": recommended_courses})

# ========================== 5️⃣ الانضمام إلى دورة ==========================
@app.route('/join_course', methods=['POST'])
@login_required
def join_course():
    """تمكين المستخدم من التسجيل في دورة"""
    try:
        data = request.get_json()
        course_id = data.get("course_id")

        if not course_id:
            return jsonify({"S": 0, "error": "يجب إدخال معرف الدورة"}), 400

        course = Course.query.get(course_id)
        if not course:
            return jsonify({"S": 0, "error": "الدورة غير موجودة"}), 404

        existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if existing_enrollment:
            return jsonify({"S": 0, "error": "أنت مسجل بالفعل في هذه الدورة"}), 400

        new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id, rating=0)
        db.session.add(new_enrollment)
        db.session.commit()
        return jsonify({"S": 1, "message": "تم التسجيل بنجاح!"}), 200
    except Exception as e:
        return jsonify({"S": 0, "error": str(e)}), 500

# ========================== 6️⃣ تقييم الدورات ==========================
@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_profile(course_id):
    """عرض معلومات الدورة وإمكانية تقييمها"""
    if current_user.id == 0:
        flash("⚠️ يجب تسجيل الدخول لتقييم الدورات!", "warning")
        return redirect(url_for('login'))

    already_reviewed = has_reviewed(course_id, current_user.id)

    if request.method == 'POST':
        rating = int(request.form['rating'])
        if add_review(course_id, rating):
            flash("✅ تم إضافة التقييم بنجاح!", "success")
        else:
            flash("⚠️ لقد قمت بالفعل بتقييم هذه الدورة!", "danger")
        return redirect(url_for('course_profile', course_id=course_id))

    course, reviews = get_course_details(course_id)
    
    return render_template('course_profile.html', course=course, reviews=reviews, user=current_user, already_reviewed=already_reviewed)





# ========================== 7️⃣  عرض نافذة اغلاق الدورة   ==========================

@app.route('/close_course/', methods=['GET'])
@login_required
def close_course():
    return render_template('close_course.html', user=current_user,id_enr=request.args.get('id_enr'))



	 
# ========================== 7️⃣   تحديث بينات اغلاق الدورة     ==========================

@app.route('/edit_close_course', methods=[ 'POST'])
@login_required
def edit_close_course():
    if request.method=='POST':
     data = request.get_json()
     grade = data.get('grade')
     id_enr = data.get('id_enr')
     hours = data.get('hours')
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
	 



# ========================== 7️⃣  صفحة عرض التوصيات حسب rating   ==========================
#  صفحة عرض التوصيات حسب rating 
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
       query = "SELECT id, course_name, description,logo,difficulty_level,gpa_requirement FROM courses WHERE id IN (%s)" % ','.join(map(str, recommended_courses[:5]))
       cursor.execute(query)
       courses = cursor.fetchall()
       conn.close()
       return jsonify({"recommended_courses": courses})



# API لاستقبال `id` الدورة وإرجاع التوصيات

@app.route('/recommendations_course/<int:course_id>', methods=['GET'])
def recommendations_course(course_id):
    recs = get_course_recommendations(course_id)
    return jsonify(recs)



#عرض جميع الدورات
@app.route('/view_courses')
@login_required
def view_courses():
    courses = Course.query.all()
    return render_template('view_courses.html', courses=courses,user=current_user)
    
    
    
    


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        course = Course(logo="def.jpg",
            course_name=request.form['course_name'],
            course_code=request.form['course_code'],
            description=request.form['description'],
            instructor=request.form['instructor'],
            credits=int(request.form['credits']),
            university=request.form['university'],
            difficulty_level=request.form['difficulty_level'],
            prerequisites=request.form['prerequisites'],
            gpa_requirement=float(request.form['gpa_requirement']) if request.form['gpa_requirement'] else None,
            language=request.form['language'],
            course_link=request.form['course_link'],
            course_url=request.form['course_url'],
            category=request.form['category']
        )
        db.session.add(course)
        db.session.commit()
        flash("Course added successfully!", "success")
        return redirect(url_for('view_courses'))

    return render_template('add_course.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_course(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.course_name = request.form['course_name']
        course.course_code = request.form['course_code']
        course.description = request.form['description']
        course.instructor = request.form['instructor']
        course.credits = int(request.form['credits'])
        course.university = request.form['university']
        course.difficulty_level = request.form['difficulty_level']
        course.prerequisites = request.form['prerequisites']
        course.gpa_requirement = float(request.form['gpa_requirement']) if request.form['gpa_requirement'] else None
        course.language = request.form['language']
        course.course_link = request.form['course_link']
        course.category = request.form['category']
        course.course_url=request.form['course_url'],
        db.session.commit()
        flash("Course updated successfully!", "success")
        return redirect(url_for('view_courses'))

    return render_template('update_course.html', course=course)

@app.route('/delete/<int:id>')
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully!", "danger")
    return redirect(url_for('index'))



    
# ========================== 7️⃣ تشغيل التطبيق ==========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ تم إنشاء الجداول في قاعدة البيانات بنجاح!")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
