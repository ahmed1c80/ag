'''
from PIL import Image
import pytesseract

# إذا كنت تستخدم Windows، قد تحتاج إلى تحديد المسار إلى tesseract.exe
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# فتح الصورة
image = Image.open('static/images/25.jpg')

# استخراج النص من الصورة
text = pytesseract.image_to_string(image, lang='ara')  # 'ara' للغة العربية

# طباعة النص المستخرج
print(text)

import pytesseract

# تحديد المسار إلى tesseract يدويًا
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # على Linux/macOS
# أو على Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# الآن يمكنك استخدام pytesseract بشكل طبيعي
from PIL import Image
text = pytesseract.image_to_string(Image.open('static/images/25.jpg'), lang='ara')
print(text)
'''

from flask import Flask, request, render_template,jsonify
import pytesseract
from PIL import Image
import os
import io
import base64

app = Flask(__name__)

# تحديد المسار إلى tesseract (إذا لزم الأمر)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# مجلد لتحميل الصور
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('ready_image.html')

@app.route('/upload2', methods=['POST'])
def upload_image2():
    if 'image' not in request.files:
        return "لم يتم تحميل أي صورة!", 400

    file = request.files['image']
    if file.filename == '':
        return "لم يتم اختيار أي ملف!", 400

    # حفظ الصورة في المجلد
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_path)

    # قراءة الصورة واستخراج النص
    try:
        text = pytesseract.image_to_string(Image.open(image_path), lang='ara')
        return f"النص المستخرج: <br><pre>{text}</pre>"
    except Exception as e:
        return f"حدث خطأ أثناء معالجة الصورة: {str(e)}", 500
        

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'لم يتم تحميل أي صورة!'}), 400

    try:
        # تحويل base64 إلى صورة
        image_data = data['image'].split(',')[1]  # إزالة الجزء الأول من base64
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # استخراج النص باستخدام pytesseract
        text = pytesseract.image_to_string(image, lang='ara')
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
'''
import pytesseract
from PIL import Image

# تحديد المسار إلى tessdata يدويًا
pytesseract.pytesseract.tesseract_cmd = r'/data/data/com.termux/files/usr/bin/tesseract'  # المسار إلى tesseract
pytesseract.pytesseract.TESSDATA_PREFIX = r'/data/data/com.termux/files/usr/share/tessdata'  # المسار إلى tessdata

# الآن يمكنك استخدام pytesseract بشكل طبيعي
text = pytesseract.image_to_string(Image.open('static/images/25.jpg'), lang='ara')
print(text)
'''