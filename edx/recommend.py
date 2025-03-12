import numpy as np
from db import add_review,get_course_details,get_db_connection,has_reviewed 
import pandas as pd
from inc import difficulty_to_val
import pymysql

from models import db, User, Course, Enrollment, Student,Grade,Preference,CoursesEdx
#import mysql.connector
#from scipy.linalg import svd


# تحميل بيانات التقييمات وتحليلها
def load_recommendation_model():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT user_id, course_id, rating FROM enrollments"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # تحويل البيانات إلى مصفوفة
    df = pd.DataFrame(data, columns=['user_id', 'course_id', 'rating'])
    ratings_matrix = df.pivot(index='user_id', columns='course_id', values='rating').fillna(0)
    ratings_np = ratings_matrix.to_numpy()

    U, sigma, Vt = np.linalg.svd(ratings_np, full_matrices=False)

    # تطبيق SVD
   # U, sigma, Vt = svd(ratings_np, full_matrices=False)
    sigma_diag = np.diag(sigma)
    print(f"*****sigma_diag {sigma_diag}")
    # إعادة بناء مصفوفة التنبؤات
    predictions = np.dot(np.dot(U, sigma_diag), Vt)
    predicted_ratings = pd.DataFrame(predictions, index=ratings_matrix.index, columns=ratings_matrix.columns)

    return predicted_ratings







def load_recommendation(user_id):

    user = User.query.filter_by(id=user_id).first()
    conn = get_db_connection()
    cursor = conn.cursor()
    #2️⃣ تنفيذ استعلام SQL لاسترداد بيانات الدورات
    query="SELECT course_name, difficulty_level, id AS course_id, gpa_requirement FROM courses"
    cursor.execute(query)
	
    #data = cursor.fetchall()
	#3️⃣ تحويل النتائج إلى قاموس يحتوي على المتجهات
    courses = {} #(course_name, difficulty_level, course_id, gpa_requirement)
    for row in cursor.fetchall():
     print(row)
     course_id = row['course_id']  # اسم الدورة
     difficulty_level = row['difficulty_level']  # اسم الدورة
# ✅ تحويل Decimal إلى float قبل الطباعة
     row['gpa_requirement'] = float(row['gpa_requirement'])
     #print(f"{course_name} {difficulty_level}")
     difficulty_level=difficulty_to_val(difficulty_level)
     vector = np.array([difficulty_level, row['gpa_requirement']])  # [الصعوبة، رقم الدورة، متطلبات GPA]
     courses[course_id] = vector
    #for cur in data:
     #courses[cur.course_name] = np.array([cur.difficulty_level, cur.gpa_requirement, cur.course_id])
  # إغلاق الاتصال بقاعدة البيانات
    cursor.close()
    conn.close()
 # 4️⃣ طباعة المتجهات للتحقق
    #for course, vector in courses.items():
      #print(f"{course}: {vector}")
	#conn.close()
  # تمثيل الطالب كمتجه
    student = np.array([user.major, float(user.gpa)])
  # تصنيف الدورات بناءً على التشابه
    #recommendations = {course: cosine_similarity(vector, student) for course, vector in courses.items()}
  # عرض التوصيات
    #sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    #for course, similarity in sorted_recommendations:
     #print(f"{course}: التشابه = {similarity:.2f}")
    # حساب التوصيات باستخدام التشابه
    recommendations = {course: cosine_similarity(vector, student) for course, vector in courses.items()}

# ترتيب التوصيات بناءً على التشابه من الأعلى إلى الأدنى
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

# استخراج جميع معرفات الدورات الموصى بها
    recommended_course_ids = [course for course, similarity in sorted_recommendations]
# استخراج جميع معرفات الدورات الموصى بها
    recommended_similarity= [similarity for course, similarity in sorted_recommendations]
    #print(f"sorted_recommendations******** {recommended_course_ids}")
    return recommended_course_ids,recommended_similarity
    
# حساب جيب التمام
def cosine_similarity(course_vector, student_vector):
    #print(f"****cosine_similarity course_vector{course_vector} student_vector{student_vector}")
    dot_product = np.dot(course_vector, student_vector)
    norm_course = np.linalg.norm(course_vector)
    norm_student = np.linalg.norm(student_vector)
    return dot_product / (norm_course * norm_student)
    
#load_recommendation()
    
# تحميل النموذج عند بدء التطبيق
predicted_ratings = load_recommendation_model()
print(f"*****predicted_ratings {predicted_ratings}")

