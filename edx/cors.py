import requests
from bs4 import BeautifulSoup
import json

   # URL الدورة
url = "https://www.coursera.org/specializations/linear-algebra-elementary-to-advanced"

   # إرسال طلب HTTP للحصول على محتوى الصفحة
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
with open("coursera_page.html", "w", encoding="utf-8") as file:
      file.write(response.text)
#print(response.content)
   # استخراج التفاصيل المطلوبة
course_details = {
       "title": soup.find('h1').text.strip(),
       "description": soup.find('div', class_='description').text.strip(),
       "instructors": [instructor.text.strip() for instructor in soup.find_all('div', class_='instructor-name')],
       "rating": soup.find('span', class_='ratings-text').text.strip(),
       "enrollment_count": soup.find('div', class_='enrollment').text.strip(),
       # يمكنك إضافة المزيد من الحقول حسب الحاجة
   }

   # تحويل القاموس إلى JSON
course_json = json.dumps(course_details, indent=4, ensure_ascii=False)

   # طباعة JSON
print(course_json)