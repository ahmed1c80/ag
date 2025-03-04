from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import numpy as np
# استيراد قاعدة البيانات من الملف الجديد
from models import db, User, Course, Enrollment#, Student

# from scipy.sparse.linalg import svds
import pymysql
def get_db_connection():
    
	return pymysql.connect(
        host='193.203.184.99',
        port=port,
		ssl=None,
		charset='utf8mb4',
        user='u804311892_agline',
        password='Ah#630540',
        database='u804311892_agline',
        cursorclass=pymysql.cursors.DictCursor
    )
	'''
    return pymysql.connect(
        host='localhost',
		charset='utf8mb4',
        user='root',
        password='rootroot',
        database='agline',
        cursorclass=pymysql.cursors.DictCursor
    )
	'''



# التحقق مما إذا كان الطالب قد قيّم الدورة بالفعل
def has_reviewed(course_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM enrollments WHERE course_id = %s AND user_id = %s"
    cursor.execute(query, (course_id, user_id))
    count = cursor.fetchone()
    #count = cursor.fetchall()
    
    conn.close()
    return count# > 0  # إذا كان هناك تقييم، يرجع True


# جلب بيانات الدورة من MySQL
def get_course_details(course_id):
    #connection = mysql.connector.connect(**db_config)
    #cursor = connection.cursor(dictionary=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    
    cursor.execute("""
        SELECT enrollments.*, users.full_name 
        FROM enrollments 
        JOIN users ON enrollments.user_id = users.id 
        WHERE course_id = %s
    """, (course_id,))
    reviews = cursor.fetchall()
	
	
    conn.close()
    return course, reviews

# إضافة تقييم جديد
def add_review(course_id, rating):
    # البحث عن المستخدم في قاعدة البيانات
    enr = Enrollment.query.filter_by(course_id=course_id,user_id=current_user.id).first()

    if enr:
       enr.rating = float(rating)  # تحديث المعدل التراكمي
       db.session.commit()  # حفظ التغييرات
       flash(f"تم تحديث GPA بنجاح إلى {enr.rating} ✅", "success")
