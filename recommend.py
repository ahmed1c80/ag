import numpy as np
import pandas as pd
import pymysql
from db import   get_db_connection 
from inc import difficulty_to_val
from models import db, User, Course, Enrollment

# 📌 تحميل بيانات التقييمات وتحليلها باستخدام SVD
def load_recommendation_model():
    """
    تحميل بيانات التقييمات من قاعدة البيانات وتحليلها باستخدام تفكيك القيم المفردة (SVD).
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # جعل النتائج على شكل قاموس ليسهل التعامل معها

    # 🔍 استعلام لاسترجاع تقييمات المستخدمين للدورات
    query = "SELECT user_id, course_id, rating FROM enrollments"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # إذا لم تكن هناك بيانات، نعيد مصفوفة فارغة
    if not data:
        print("⚠️ لا توجد بيانات تقييم متاحة!")
        return pd.DataFrame()

    # 🟢 تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data, columns=['user_id', 'course_id', 'rating'])

    # 🟢 إنشاء مصفوفة المستخدم-الدورة (Pivot Table)
    ratings_matrix = df.pivot(index='user_id', columns='course_id', values='rating').fillna(0)
    ratings_np = ratings_matrix.to_numpy()

    # 🔍 تطبيق SVD لتحليل المصفوفة
    U, sigma, Vt = np.linalg.svd(ratings_np, full_matrices=False)
    sigma_diag = np.diag(sigma)  # تحويل المصفوفة القطرية إلى مصفوفة كاملة

    # 🟢 إعادة بناء مصفوفة التوقعات
    predictions = np.dot(np.dot(U, sigma_diag), Vt)

    # 🟢 تحويل المصفوفة إلى DataFrame لمطابقة المستخدمين والدورات
    predicted_ratings = pd.DataFrame(predictions, index=ratings_matrix.index, columns=ratings_matrix.columns)

    return predicted_ratings


# 📌 حساب التشابه الكوزايني بين متجه الطالب ومتجه الدورة
def cosine_similarity(course_vector, student_vector):
    """
    حساب التشابه بين متجه الطالب ومتجه الدورة باستخدام جيب التمام (Cosine Similarity).
    """
    dot_product = np.dot(course_vector, student_vector)
    norm_course = np.linalg.norm(course_vector)
    norm_student = np.linalg.norm(student_vector)

    # 🟢 التحقق من عدم القسمة على صفر
    if norm_course == 0 or norm_student == 0:
        return 0

    return dot_product / (norm_course * norm_student)




def load_recommendation(user_id):
    """
    تحميل توصيات الدورات بناءً على بيانات الطالب والتشابه الكوزايني،
    مع استبعاد الدورات التي سبق تسجيلها.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        print(f"⚠️ المستخدم ID {user_id} غير موجود!")
        return [], []

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # نتائج على شكل قاموس

    # 🔍 استعلام لاسترجاع تفاصيل الدورات مع استبعاد الدورات المسجلة مسبقًا
    query = """
    SELECT id AS course_id, course_name, difficulty_level, gpa_requirement 
    FROM courses 
    WHERE id NOT IN (
        SELECT course_id FROM enrollments WHERE user_id = %s
    )
    """
    
    cursor.execute(query, (user_id,))
    courses_data = cursor.fetchall()
    cursor.close()
    conn.close()

    if not courses_data:
        print("⚠️ لا توجد دورات متاحة للتوصية!")
        return [], []

    # 🟢 تحويل بيانات الدورات إلى قاموس يحتوي على المتجهات
    courses = {}
    for row in courses_data:
        course_id = row['course_id']
        difficulty_level = difficulty_to_val(row['difficulty_level'])  # تحويل مستوى الصعوبة إلى قيمة عددية
        gpa_requirement = float(row['gpa_requirement']) if row['gpa_requirement'] is not None else 0.0

        # إنشاء متجه الدورة [الصعوبة، متطلبات GPA]
        vector = np.array([difficulty_level, gpa_requirement])
        courses[course_id] = vector

    # 🟢 تمثيل الطالب كمتجه [التخصص، GPA]
    student_vector = np.array([user.major, float(user.gpa)])

    # 🔍 حساب التشابه الكوزايني لكل دورة
    recommendations = {
        course_id: cosine_similarity(vector, student_vector)
        for course_id, vector in courses.items()
    }

    # 🟢 ترتيب الدورات بناءً على التشابه من الأعلى إلى الأدنى
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

    # 🟢 استخراج جميع معرفات الدورات الموصى بها والتشابه المقابل
    recommended_course_ids = [course for course, _ in sorted_recommendations]
    recommended_similarities = [similarity for _, similarity in sorted_recommendations]

    return recommended_course_ids, recommended_similarities



#استدعاء الدورات المرتبطة بالطالب
def getcoursersStudent(user_id):
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
    conn.close()
    return 	courses


# ✅ تحميل النموذج عند بدء التطبيق
predicted_ratings = load_recommendation_model()
if not predicted_ratings.empty:
    print(f"🔹 مصفوفة التنبؤات:\n{predicted_ratings}")
else:
    print("⚠️ لم يتم إنشاء مصفوفة التنبؤات بسبب نقص البيانات.")
