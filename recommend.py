import numpy as np
from db import add_review,get_course_details,get_db_connection,has_reviewed 
import pandas as pd
import pymysql
#import mysql.connector
#from scipy.linalg import svd


# تحميل بيانات التقييمات وتحليلها
def load_recommendation_model():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT user_id, course_id, rating FROM enrollments"
    cursor.execute(query)
    data = cursor.fetchall()
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







def load_recommendation():
  # تمثيل الدورات كمتجهات
  courses = {
    "الجبر الخطي 1": np.array([1, 2.5]),
    "تحليل المصفوفات": np.array([2, 3.0]),
    "الجبر الخطي وتعلم الآلة": np.array([3, 3.5]),
    
  }
  # تمثيل الطالب كمتجه
  student = np.array([2, 3.2])
  # تصنيف الدورات بناءً على التشابه
  recommendations = {course: cosine_similarity(vector, student) for course, vector in courses.items()}
  # عرض التوصيات
  sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
  for course, similarity in sorted_recommendations:
    print(f"{course}: التشابه = {similarity:.2f}")
    
# حساب جيب التمام
def cosine_similarity(course_vector, student_vector):
    dot_product = np.dot(course_vector, student_vector)
    norm_course = np.linalg.norm(course_vector)
    norm_student = np.linalg.norm(student_vector)
    return dot_product / (norm_course * norm_student)
    
load_recommendation()
    
# تحميل النموذج عند بدء التطبيق
predicted_ratings = load_recommendation_model()
print(f"*****predicted_ratings {predicted_ratings}")