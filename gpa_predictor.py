import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
# إعادة تدريب النموذج
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# توليد بيانات تجريبية
np.random.seed(42)
num_samples = 1000
X = np.random.rand(num_samples, 5)
y = np.random.rand(num_samples, 1) * 4  # المعدل التراكمي بين 0 و 4

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# تطبيع البيانات
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# حفظ المحول القياسي
joblib.dump(scaler, "scaler.pkl")

# بناء النموذج
model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1)  
])

# تجميع وتدريب النموذج
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# حفظ النموذج
model.save("gpa_predictor.h5")
print("✅ النموذج تم حفظه بنجاح!")
