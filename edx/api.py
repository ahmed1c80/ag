import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from bs4 import BeautifulSoup

import requests
app = Flask(__name__)

#جلب الدورات من الويب

def get_api_coursers():
# استبدل 'your_access_token' بالتوكن الذي حصلت عليه
       access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJyaW5teWJ5ZWRudWF3NXBobGlkQ29jRHVkYnlsYk9iRGliSm9kYm9zZ2V0c0ViYWxkNCIsImV4cCI6MTc0MTQ2OTAyNCwiZ3JhbnRfdHlwZSI6ImNsaWVudC1jcmVkZW50aWFscyIsImlhdCI6MTc0MTQ2NTQyNCwiaXNzIjoiaHR0cHM6Ly9jb3Vyc2VzLmVkeC5vcmcvb2F1dGgyIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWhtZWQxYzgwIiwic2NvcGVzIjpbInJlYWQiLCJ3cml0ZSIsImVtYWlsIiwicHJvZmlsZSJdLCJ2ZXJzaW9uIjoiMS4yLjAiLCJzdWIiOiI3Nzc1NDBkYmJiMzg2NGE1Nzk0MDhlMzJjNmYyM2I5ZSIsImZpbHRlcnMiOltdLCJpc19yZXN0cmljdGVkIjpmYWxzZSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImVtYWlsIjoiYWhtZWQxYzgwQGdtYWlsLmNvbSIsIm5hbWUiOiJBaG1lZCBGYWdlaCIsImZhbWlseV9uYW1lIjoiRmFnZWgiLCJnaXZlbl9uYW1lIjoiQWhtZWQiLCJhZG1pbmlzdHJhdG9yIjpmYWxzZSwic3VwZXJ1c2VyIjpmYWxzZX0.WzvDnI2G98uBIFjYXM-MIPHph9i2veO7OOhW2UGthKk'
       headers = {
    'Authorization': f'Bearer {access_token}'
       }

# نقطة النهاية لجلب معلومات الدورات
       url = 'https://api.edx.org/catalog/v1/courses'

# إرسال الطلب مع المعلمات المناسبة
       params = {'search': 'linear algebra'}
       response = requests.get(url, headers=headers, params=params)
       print(response)
# التحقق من حالة الاستجابة
       if response.status_code == 200:
         courses = response.json()
         for course in courses['results']:
          print(f"Course ID: {course['id']}")
          print(f"Course Name: {course['title']}")
          print(f"Course Description: {course['short_description']}\n")
       else:
        print(f"Failed to retrieve courses. Status code: {response.status_code}")
       return render_template('myfile2.html')
#جلب الدورات من الويب
@app.route('/get_courses_web')
def get_courses_web():
       return render_template('myfile2.html')
       COURSES_URL="https://ocw.mit.edu/search/?q=Linear+Algebra"
       response = requests.get(COURSES_URL)
#print(response.text)
       with open("templates/myfile2.html", "w") as file:
         file.write(response.text)
         file.write('<link type="text/css"  href="static/style2.css" rel="stylesheet">')
         if response.status_code == 200:
          soup = BeautifulSoup(response.text, "html.parser")
          styles = soup.find_all("style")
          data_style="";
          for style in styles[:10]:
            with open("style2.css", "w") as file:
               file.write(style.text)
     #  data_style+= style #").strip()}")
     #  x+1 
         else:
          print("no style")
       return render_template('myfile2.html')
       
       # ✅ API لجلب الدورات من Udemy أو Coursera

@app.route('/api/web_courses', methods=['GET'])

def get_web_courses():
    query = request.args.get("query", "Linear Algebra")
    
    # 🔹 استعلام Udemy API
    udemy_url = "https://www.udemy.com/api-2.0/courses/"
    udemy_params = {"search": query, "page_size": 5}
    udemy_headers = {"Authorization": "Bearer YOUR_UDEMY_API_KEY"}

    udemy_response = requests.get(udemy_url, params=udemy_params, headers=udemy_headers)
    udemy_courses = udemy_response.json().get("results", []) if udemy_response.status_code == 200 else []

    # 🔹 تجميع النتائج
    recommendations = [{"title": c["title"], "url": c["url"], "platform": "Udemy"} for c in udemy_courses]

    return jsonify(recommendations)


