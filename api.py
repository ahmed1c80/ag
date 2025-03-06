import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from bs4 import BeautifulSoup

import requests
app = Flask(__name__)

#جلب الدورات من الويب

def get_api_coursers():
# استبدل 'your_access_token' بالتوكن الذي حصلت عليه
       access_token = 'nueLytFReVvnPIaxj8y9dulwSCiYbIYdU0WtHyQra0WwcnTXtx6Ey02KFTHH'
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


