#تطبيق نظام توصيات ذكي باستخدام SVD (تفكيك القيم المفردة)
# SVD (Singular Value Decomposition) هو خوارزمية مستخدمة في أنظمة التوصية، مثل Netflix و YouTube، لتحليل أنماط المستخدمين وتقديم توصيات دقيقة.
# تنفيذ خوارزمية SVD في Flask

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from flask import Flask, jsonify

app = Flask(__name__)

# بيانات افتراضية للمستخدمين والدورات التي سجلوها
data = {
    "user_id": [1, 1, 2, 2, 3, 3, 4, 4],
    "course_id": [101, 102, 101, 103, 102, 104, 103, 105],
    "rating": [4, 5, 3, 4, 2, 5, 3, 4]  # تقييمات الدورات
}

df = pd.DataFrame(data)

# إنشاء مصفوفة المستخدمين والدورات
user_course_matrix = df.pivot(index="user_id", columns="course_id", values="rating").fillna(0)

# تطبيق SVD لاستخراج الأنماط
svd = TruncatedSVD(n_components=2)  # تخفيض الأبعاد
user_factors = svd.fit_transform(user_course_matrix)

#@app.route('/recommend/<int:user_id>')
def get_recommend(user_id):
    if user_id not in user_course_matrix.index:
        return jsonify({"error": "User not found"}), 404
    
    user_index = user_course_matrix.index.get_loc(user_id)
    user_vector = user_factors[user_index]  # استخراج عامل المستخدم
    course_scores = np.dot(user_vector, svd.components_)  # حساب التوصيات
    
    recommended_courses = np.argsort(-course_scores)[:30]  # أفضل 3 دورات
    print("****recommended_courses.json")
    print(recommended_courses.tolist())
    return jsonify({"recommended_courses": recommended_courses.tolist()})

#if __name__ == '__main__':
 #   app.run(debug=True)

# كيف يعمل؟
#يحلل الأنماط المخفية من تفاعلات الطلاب مع الدورات.
#يقترح أفضل الدورات بناءً على أوجه التشابه بين الطلاب الآخرين.
#يوفر توصيات مخصصة بناءً على تاريخ الدراسة.
