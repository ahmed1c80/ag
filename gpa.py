import numpy as np
from db import get_db_connection
from inc import grade_to_gpa

def getdata(user_id):
    """
    جلب بيانات الطالب من قاعدة البيانات بناءً على user_id.

    Args:
        user_id (int): معرف المستخدم (الطالب).

    Returns:
        list: قائمة من القواميس تحتوي على بيانات الطالب.
    """
    db = get_db_connection()
    cursor = db.cursor()#(dictionary=True)  # استخدام dictionary=True لجلب البيانات كقواميس
    # جلب البيانات من جدول enrollments للطالب المحدد
    cursor.execute("""
        SELECT user_id, course_id, grade, rating, hours 
        FROM enrollments 
        WHERE completed = 1 AND enrollments.user_id = %s
        """, (user_id,))
    data = cursor.fetchall()  # البيانات كقائمة من القواميس
    #print("البيانات الخام من قاعدة البيانات:")
    print(data)
    cursor.close()
    db.close()
    return data

# تحويل البيانات إلى مصفوفة numpy
def convert_to_numpy2(data):
    # استخراج القيم من القواميس
    user_ids = [row['user_id'] for row in data]
    course_ids = [row['course_id'] for row in data]
    grades = [row['grade'] for row in data]
    ratings = [row['rating'] for row in data]
    hours = [row['hours'] for row in data]

    # إنشاء مصفوفة numpy ثنائية الأبعاد
    data_array = np.column_stack((user_ids, course_ids, grades, ratings, hours))
    return data_array

def convert_to_numpy(data):
    """
    تحويل البيانات من قائمة القواميس إلى مصفوفة numpy.

    Args:
        data (list): قائمة من القواميس تحتوي على بيانات الطالب.

    Returns:
        numpy.ndarray: مصفوفة numpy ثنائية الأبعاد تحتوي على البيانات.
    """
    # استخراج القيم من القواميس
    user_ids = [int(row['user_id']) for row in data]
    course_ids = [int(row['course_id']) for row in data]
    grades = [row['grade'] for row in data]  # الدرجات قد تكون نصوصًا (مثل 'A', 'B')
    ratings = [float(row['rating']) for row in data]
    hours = [float(row['hours']) for row in data]

    # إنشاء مصفوفة numpy ثنائية الأبعاد
    data_array = np.column_stack((user_ids, course_ids, grades, ratings, hours))
    return data_array



# حساب المعدل التراكمي
def calculate_gpa(data):
    """
    حساب المعدل التراكمي (GPA) للطلاب بناءً على بياناتهم.

    Args:
        data (numpy.ndarray): مصفوفة numpy تحتوي على بيانات الطلاب.

    Returns:
        numpy.ndarray: مصفوفة numpy تحتوي على معرف الطالب والمعدل التراكمي.
    """
    user_ids = np.unique(data[:, 0])  # الحصول على جميع user_id الفريدة
    gpa_list = []

    for user_id in user_ids:
        user_data = data[data[:, 0] == user_id]  # تصفية بيانات الطالب
        user_data[:, 4] = user_data[:, 4].astype(float)  # تحويل الساعات إلى float
        user_data[:, 5] = user_data[:, 5].astype(float)  # تحويل النقاط إلى float

        total_points = np.sum(user_data[:, 5].astype(float) * user_data[:, 4].astype(float))  # النقاط × الساعات
        total_hours = np.sum(user_data[:, 4].astype(float))  # مجموع الساعات
        gpa = total_points / total_hours if total_hours > 0 else 0
        gpa = convert_float(gpa)
        gpa_list.append((user_id, gpa))

    return np.array(gpa_list)

def convert_float(gpa):
    """
    تقريب المعدل التراكمي إلى منزلة عشرية واحدة.

    Args:
        gpa (float): المعدل التراكمي الخام.

    Returns:
        float: المعدل التراكمي المقرّب إلى منزلة عشرية واحدة.
    """
    formatted_number = float(f"{gpa:.1f}")
    return formatted_number

def getgpauser(user_id):
    """
    حساب المعدل التراكمي (GPA) لطالب معين.

    Args:
        user_id (int): معرف المستخدم (الطالب).

    Returns:
        numpy.ndarray: مصفوفة numpy تحتوي على معرف الطالب والمعدل التراكمي.
    """
    data = getdata(user_id)
    data_array = convert_to_numpy(data)
    print("البيانات كـ numpy array:")
    print(data_array)
    # تحويل الدرجات إلى نقاط GPA
    gpa_points = np.array([grade_to_gpa(grade) for grade in data_array[:, 2]])
    data_array = np.column_stack((data_array, gpa_points))  # إضافة عمود النقاط
    print("البيانات مع النقاط:")
    print(data_array)
    gpa_data = calculate_gpa(data_array)
    print("المعدل التراكمي لكل طالب:")
    print(gpa_data)
    return gpa_data