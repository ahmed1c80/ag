from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import numpy as np
# استيراد قاعدة البيانات من الملف الجديد
from models import db, User, Course, Enrollment#, Student
import inc as grade_to_gpa
# from scipy.sparse.linalg import svds
import pymysql

port = 3306  # تأكد من أنه عدد صحيح

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



# جلب بيانات الدورة من MySQLEdx
def get_course_details_edx(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM coursers_edx WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    
    cursor.execute("""
        SELECT enrollments.*, users.full_name 
        FROM enrollments 
        JOIN users ON enrollments.user_id = users.id 
        WHERE edx_id = %s
    """, (course_id,))
    reviews = cursor.fetchall()
	
	
    conn.close()
    return course, reviews

# جلب بيانات الدورة من MySQL
def get_course_details(course_id):
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
    print(enr)
    if enr:
       enr.rating = float(rating)  # تحديث المعدل التراكمي
       db.session.commit()  # حفظ التغييرات
       #flash(f"تم تحديث GPA بنجاح إلى {enr.rating} ✅", "success")


def getchartdata(user_id):
  conn = get_db_connection()

  cursor = conn.cursor()
  # جلب البيانات
  cursor.execute("""
    SELECT user_id, course_id, grade, rating, hours ,course_name
    FROM enrollments JOIN courses ON courses.id = enrollments.course_id  
    WHERE enrollments.completed = 1 AND enrollments.user_id = %s
    """, (user_id,))
  rows = cursor.fetchall()  # البيانات كقائمة من الصفوف
    # تحويل البيانات إلى قائمة من القواميس
  columns = ["user_id", "course_id", "grade", "rating", "hours"]
  data =rows# [dict(zip(columns, row)) for row in rows]
  grade_map = {
        'A+': 5.0,
        'A': 4.75,
        'B+': 4.5,
        'B': 4.0,
        'C+': 3.5,
        'C': 3.0,
        'D+': 2.5,
        'D': 2.0,
        'F': 1.0
    }
  labels = [course['course_name'] for course in data]
  values = [course['grade'] for course in data]
  gpa_values = [grade_map.get(grade, 0.0) for grade in values]
  data = {
        "understanding": {
            "labels":labels ,
            "values": gpa_values  # نسبة الفهم لكل دورة
        },
        "weakness": {
            "labels": ["تفاضل وتكامل", "إحصاء", "برمجة"],  # المواد التي بها نقاط ضعف
            "values": [0, 0, 0]  # نسبة الضعف في كل مادة
        }
    }
  #print(data)
  return data;

#getchartdata(3)