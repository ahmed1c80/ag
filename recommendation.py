import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from models import db,User,Course,Enrollment  # استيراد قاعدة البيانات من الملف الجديد
from flask_sqlalchemy import SQLAlchemy
#from app import db, Student

def get_recommendations(user_id):
    students = Student.query.all()
    
    # تحويل البيانات إلى DataFrame
    data = pd.DataFrame([{
        'gpa': student.gpa,
        'major': student.major,
        'interests': student.interests
    } for student in students])

    # تحويل النصوص إلى قيم عددية
    label_enc = LabelEncoder()
    data['major'] = label_enc.fit_transform(data['major'])
    
    interests_vectorized = data['interests'].apply(lambda x: len(x.split()))
    data['interests_vectorized'] = interests_vectorized

    # توحيد البيانات
    scaler = StandardScaler()
    data[['gpa', 'major', 'interests_vectorized']] = scaler.fit_transform(data[['gpa', 'major', 'interests_vectorized']])

    # بناء نموذج شبكة عصبية بسيطة
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation='relu', input_shape=(3,)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    print("****",model)

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # تحويل البيانات إلى مصفوفات NumPy للتدريب
    X_train = data[['gpa', 'major', 'interests_vectorized']].values
    y_train = np.random.randint(0, 2, size=len(data))

    model.fit(X_train, y_train, epochs=10, verbose=0)

    # إعطاء توصيات للمستخدم الحالي
    user = Student.query.filter_by(id=user_id).first()
    if user:
        user_data = np.array([[user.gpa, label_enc.transform([user.major])[0], len(user.interests.split())]])
        user_data = scaler.transform(user_data)
        recommendation_score = model.predict(user_data)[0][0]
	
        return recommendation_score# "نوصي بهذه الدورة" if recommendation_score > 0.5 else "جرب دورة أخرى"
    return "لم يتم العثور على بيانات للطالب"
