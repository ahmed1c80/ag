# يمكن استخدام شبكة عصبية بسيطة (MLP - Multi-Layer Perceptron) لتوقع المعدل التراكمي للطالب (GPA) بناءً على بياناته السابقة.

#✅ تنفيذ نموذج تعلم عميق (MLP) لتوقع GPA
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

app = Flask(__name__)

# إنشاء نموذج شبكة عصبية
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(3,)),  # 3 ميزات: عدد الدورات، عدد الساعات، متوسط التقييمات
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)  # مخرجات واحدة وهي توقع الـ GPA
])

model.compile(optimizer='adam', loss='mse')

# بيانات تدريب افتراضية
X_train = np.array([[5, 15, 4.2], [6, 18, 3.8], [4, 12, 4.5]])  # [عدد الدورات، الساعات، متوسط التقييمات]
y_train = np.array([3.7, 3.5, 3.9])  # GPA الفعلي

model.fit(X_train, y_train, epochs=50, verbose=0)  # تدريب النموذج

@app.route('/predict_gpa', methods=['POST'])
def predict_gpa():
    data = request.json
    features = np.array([[data['courses'], data['hours'], data['avg_rating']]])
    
    predicted_gpa = model.predict(features)[0][0]  # توقع GPA
    
    return jsonify({"predicted_gpa": round(predicted_gpa, 2)})

if __name__ == '__main__':
    app.run(debug=True)

# كيف يعمل؟
#يتوقع GPA بناءً على:
#عدد الدورات التي درسها الطالب
#عدد الساعات المكتسبة
#متوسط تقييمات الدورات التي درسها
#يمكن توسيع النموذج ليشمل العوامل السلوكية وطرق التعلم.
