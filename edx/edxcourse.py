import requests

# بيانات الاعتماد
#client_id = '4XFPFh2yVUZLEcwZNYJXcoeOSD7Z297FAiakybUq'
#client_secret = 'PB23HYz4qZUZJmtklsPbShLPN0C7tLHKhLCMsLCSkEB3Zjtb8HD0xXfdZM0temk0nIscg73CPg8VmHEWE7jxIzJATqsFn0zzL3rJg9KApWHmRd8LUYp84RK5lBOEmaFy'
client_id = 'wzBtcAasJuAYZmoVzz8wmroaXcWxa2L5ydvhavfS'
client_secret = 'ANlQhPRVeFS2pepPG0Ot2iva77wiklWs4QgYot0c3Ui4tzMQcwWjtblo5iYUJjcN1eBnUvI6EXNqVSrLp2NBlJTU3L2StbVuKMZxI14TooMcmk4liX3t6Nfp2uYKmnzz'
token_url = 'https://courses.edx.org/oauth2/access_token'

# الحصول على رمز الوصول
def get_access_token(client_id, client_secret, token_url):
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'token_type': 'jwt'
    }
    response = requests.post(token_url, data=data)
    response_data = response.json()
    return response_data.get('access_token')

# جلب بيانات الدورة
def get_course_details(access_token, course_id):
    course_url = f'https://courses.edx.org/api/courses/v1/courses/{course_id}'
    headers = {
        'Authorization': f'JWT {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(course_url, headers=headers)
    print(response.json())
    return response.json()
# جلب بيانات الكتل (Blocks)
def get_course_blocks(access_token, course_id, username=None):
    blocks_url = f'https://courses.edx.org/api/courses/v1/blocks/?course_id={course_id}'
    headers = {
        'Authorization': f'JWT {access_token}',
        'Accept': 'application/json'
    }
    params = {}
    if username:
        params['username'] = username  # توفير اسم المستخدم
    else:
        params['all_blocks'] = True  # جلب جميع الكتل

    response = requests.get(blocks_url, headers=headers, params=params)
    print(response.json())
    return response.json()

# عرض تفاصيل الدورة
def display_course_details(course):
    print(f"اسم الدورة: {course.get('name')}")
    print(f"معرف الدورة: {course.get('id')}")
    print(f"المنظمة: {course.get('org')}")
    print(f"تاريخ البدء: {course.get('start')}")
    print(f"الوصف: {course.get('short_description')}")
    print(f"رابط صورة البانر: {course.get('media', {}).get('banner_image', {}).get('uri_absolute')}")
    print(f"رابط فيديو الدورة: {course.get('media', {}).get('course_video', {}).get('uri')}")

# الدالة الرئيسية
def getprofilecourseedx(course_id):
    # الحصول على رمز الوصول
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        print("فشل في الحصول على رمز الوصول.")
        return

    # معرف الدورة (Course ID)
    #course_id = 'course-v1:HarvardX+CS50x+2021'  # استبدل بمعرف الدورة الفعلي
    #course_id = 'ccx-v1:adam+Mac_APccx+e0d+ccx@3'  # استبدل بمعرف الدورة الفعلي
    #course = get_course_blocks(access_token, course_id)
    # جلب بيانات الدورة
    course = get_course_details(access_token, course_id)
    return course
    # عرض تفاصيل الدورة
    display_course_details(course)

# تشغيل البرنامج
#if __name__ == "__main__":
#    main()
    
    
    


  