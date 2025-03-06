import numpy as np
from db import add_review,get_course_details,get_db_connection,has_reviewed 
import pandas as pd

import mysql.connector
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

    # إعادة بناء مصفوفة التنبؤات
    predictions = np.dot(np.dot(U, sigma_diag), Vt)
    predicted_ratings = pd.DataFrame(predictions, index=ratings_matrix.index, columns=ratings_matrix.columns)

    return predicted_ratings

# تحميل النموذج عند بدء التطبيق
predicted_ratings = load_recommendation_model()
print(predicted_ratings)