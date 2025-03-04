# تحسين تحليل الأداء باستخدام الذكاء الاصطناعي
# يمكن تحليل أداء الطلاب بعمق وتقديم نقاط القوة والضعف لكل طالب.
# استخدام Random Forest لتوقع أداء الطالب في الدورات القادمة
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestRegressor
import numpy as np

app = Flask(__name__)

# بيانات تدريب افتراضية
X_train = np.array([[3.5, 4, 85], [3.8, 5, 90], [3.2, 3, 78]])  # [GPA, عدد الدورات, النسبة المئوية للاختبارات]
y_train = np.array([88, 92, 76])  # أداء الطالب المتوقع

# تدريب نموذج Random Forest
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

@app.route('/predict_performance', methods=['POST'])
def predict_performance():
    data = request.json
    features = np.array([[data['gpa'], data['courses'], data['exam_percent']]])
    
    predicted_performance = model.predict(features)[0]  # توقع أداء الطالب
    
    return jsonify({"predicted_performance": round(predicted_performance, 2)})

if __name__ == '__main__':
    app.run(debug=True)

# كيف يعمل؟
#يتنبأ بمستوى أداء الطالب في المقررات القادمة.
#يساعد المعلمين على فهم نقاط ضعف الطلاب.
