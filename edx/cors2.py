import requests
from bs4 import BeautifulSoup
import json
from inc import to_name_file

# رابط الدورة
     #url = "https://www.coursera.org/specializations/linear-algebra-elementary-to-advanced"

def getcoursera(url):
  # تحميل محتوى الصفحة
        response = requests.get(url)
        cont=subshtml(response.content)
        print(f"*******cont {cont}")
        soup = BeautifulSoup(response.content, 'html.parser')
        title=soup.find("title").text.strip()
        print(f"****title{to_name_file(title)}")
        with open(f"static/coursera/{to_name_file(title)}.html", "w", encoding="utf-8") as file:
         file.write(cont)
        # استخراج البيانات
        course_details = {
    "title": soup.find("h1", {"class": "cds-119"}).text.strip(),
    "institution": soup.find("img", {"alt": "Johns Hopkins University"})['alt'],
    "description": soup.find("p", {"class": "css-4s48ix"}).text.strip(),
    "skills_you_will_gain": [skill.text.strip() for skill in soup.find_all("a", {"class": "cds-119"})],
    "details": {
        "level": soup.find("div", {"class": "css-fk6qfz"}).text.strip(),
        "duration": soup.find("div", {"class": "css-fk6qfz"}).find_next("div").text.strip(),
        "language": soup.find("div", {"class": "css-onm9p2"}).text.strip(),
        "certificate": soup.find("div", {"class": "css-1qfxccv"}).text.strip()
    },
    "courses": [
        {
            "title": course.find("h3", {"class": "cds-119"}).text.strip(),
            "duration": course.find("span", {"class": "css-13ciukr"}).text.strip(),
            "rating": course.find("span", {"class": "css-15ld0c5"}).text.strip()
        }
        for course in soup.find_all("div", {"class": "css-3glzp7"})
    ],
    "faqs": [
        {
            "question": faq.find("span", {"class": "css-6ecy9b"}).text.strip(),
            "answer": faq.find("div", {"class": "css-gvhm8"}).text.strip()
        }
        for faq in soup.find_all("div", {"class": "css-fgk7n6"})
    ]
    }
    # تحويل البيانات إلى JSON
        json_data = json.dumps(course_details, indent=4)
    # حفظ البيانات في ملف JSON
        with open(f"static/coursera/{to_name_file(title)}.json", "w") as json_file:
          json_file.write(json_data)
          print("تم استخراج البيانات وحفظها في ملف course_details.json")
          return json_data



def subshtml(html_content):
  # تحليل HTML باستخدام BeautifulSoup
  soup = BeautifulSoup(html_content, 'html.parser')
  # البحث عن جميع عناصر <script>
  scripts = soup.find_all('script')
  #return scripts
  # استخراج البيانات من <script>
  for script in scripts:
    if script.string:  # التأكد من أن العنصر يحتوي على نص
     script_text = script.string
     
     #print(f"*****script_text {script_text}")
     # البحث عن بيانات محددة باستخدام تعبيرات عادية
     if "!function(e){function webpackJsonpCallback(c){" in script_text:
       return script_text
       print(f"*****window.__DATA__ {window.__DATA__}")
       # استخراج JSON من النص
       match = re.search(r'window\.__DATA__\s*=\s*(\{.*?\});', script_text)
       if match:
         return match.group(1)
         json_data = match.group(1)
         print("تم العثور على البيانات:", json_data)