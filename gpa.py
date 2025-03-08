import mysql.connector
import numpy as np
from db import add_review,get_course_details,get_db_connection,has_reviewed 
# الاتصال بقاعدة البيانات
from inc import grade_to_gpa
db=get_db_connection();


def getdata(user_id):
  cursor = db.cursor()  # جلب البيانات كقائمة من الصفوف
  # جلب البيانات
  cursor.execute("""
    SELECT user_id, course_id, grade, rating, hours 
    FROM enrollments 
    WHERE completed = 1 AND enrollments.user_id = %s
    """, (user_id,))
  rows = cursor.fetchall()  # البيانات كقائمة من الصفوف
    # تحويل البيانات إلى قائمة من القواميس
  columns = ["user_id", "course_id", "grade", "rating", "hours"]
  data =rows# [dict(zip(columns, row)) for row in rows]
  print("البيانات كقائمة من القواميس:")
  print(data)
  return data;

# تحويل البيانات إلى مصفوفة numpy
def convert_to_numpy(data):
    # استخراج القيم من القواميس
    user_ids = [row['user_id'] for row in data]
    course_ids = [row['course_id'] for row in data]
    grades = [row['grade'] for row in data]
    ratings = [row['rating'] for row in data]
    hours = [row['hours'] for row in data]

    # إنشاء مصفوفة numpy ثنائية الأبعاد
    data_array = np.column_stack((user_ids, course_ids, grades, ratings, hours))
    return data_array



# حساب المعدل التراكمي
def calculate_gpa(data):
    user_ids = np.unique(data[:, 0])  # الحصول على جميع user_id الفريدة
    gpa_list = []

    for user_id in user_ids:
        user_data = data[data[:, 0] == user_id]  # تصفية بيانات الطالب
        user_data[:, 4] = user_data[:, 4].astype(int)  # تحويل الساعات إلى float
        user_data[:, 5] = user_data[:, 5].astype(float)  # تحويل النقاط إلى float

        total_points = np.sum(user_data[:, 5].astype(float) * user_data[:, 4].astype(float) )  # النقاط × الساعات
        total_hours = np.sum(user_data[:, 4].astype(float) )  # مجموع الساعات
        gpa = total_points / total_hours if total_hours > 0 else 0
        gpa=convert_float(gpa)
        gpa_list.append((user_id, gpa))

    return np.array(gpa_list)

def convert_float(gpa):
  formatted_number = float(f"{gpa:.1f}")
  return formatted_number # Output: 4.4

def getgpauser(user_id):
 data=getdata(user_id)
 data_array = convert_to_numpy(data)
 print("البيانات كـ numpy array:")
 print(data_array)
 # تطبيق الدالة على البيانات
 gpa_points = np.array([grade_to_gpa(grade) for grade in data_array[:, 2]])
 data_array = np.column_stack((data_array, gpa_points))  # إضافة عمود النقاط
 print("البيانات مع النقاط:")
 print(data_array)
 gpa_data = calculate_gpa(data_array)
 print("المعدل التراكمي لكل طالب:")
 print(gpa_data)
 return gpa_data

#getgpauser(3)