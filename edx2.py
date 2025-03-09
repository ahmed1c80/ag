import requests
from models import CoursesEdx,db
import base64

# بيانات الاعتماد (Client ID و Client Secret)
#client_id = '4XFPFh2yVUZLEcwZNYJXcoeOSD7Z297FAiakybUq'
#client_secret = 'PB23HYz4qZUZJmtklsPbShLPN0C7tLHKhLCMsLCSkEB3Zjtb8HD0xXfdZM0temk0nIscg73CPg8VmHEWE7jxIzJATqsFn0zzL3rJg9KApWHmRd8LUYp84RK5lBOEmaFy'
client_id = 'wzBtcAasJuAYZmoVzz8wmroaXcWxa2L5ydvhavfS'
client_secret = 'ANlQhPRVeFS2pepPG0Ot2iva77wiklWs4QgYot0c3Ui4tzMQcwWjtblo5iYUJjcN1eBnUvI6EXNqVSrLp2NBlJTU3L2StbVuKMZxI14TooMcmk4liX3t6Nfp2uYKmnzz'
token_url = 'https://courses.edx.org/oauth2/access_token'

# دالة للحصول على رمز الوصول (Access Token)
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


def search_edx_courses(access_token, search_query):
  # عنوان API الخاص بـ edX لاسترداد الدورات
    API_URL = "https://api.edx.org/catalog/v1/courses/"
    encoded_key = base64.b64encode(access_token.encode()).decode()
   # ضع مفتاح API الخاص بك هنا إذا كان مطلوبًا
    HEADERS = {
    "Authorization": f"Bearer {encoded_key}"  # استبدل YOUR_EDX_API_KEY بمفتاحك الفعلي
    }
    params = {
        "search": search_query,  # البحث عن كلمة مفتاحية
        "limit": 5        # عدد النتائج المراد استردادها
    }
    
    response = requests.get(API_URL, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        courses = response.json().get("results", [])
        for course in courses:
            print(f"📌 العنوان: {course['title']}")
            print(f"📖 الوصف: {course.get('short_description', 'لا يوجد وصف')}")
            print(f"🔗 رابط الدورة: {course.get('marketing_url', 'غير متوفر')}")
            print("-" * 50)
    else:
        print(f"❌ خطأ: {response.status_code}, {response.text}")
# دالة للبحث عن الدورات باستخدام كلمة مفتاحية
def search_courses(access_token, search_query):
    search_url = 'https://courses.edx.org/api/courses/v1/courses'
    #search_url = "https://api.edx.org/catalog/v1/courses/"
    #search_url='https://api.edx.org/catalog/v1/catalogs/'
    headers = {
        'Authorization': f'JWT {access_token}',
        'Accept': 'application/json'
    }
    params = {
    'search_term': 'Linear Algebra',
    'org': 'MITx',
    'page_size': 50  # زيادة عدد النتائج في الصفحة الواحدة

          # إضافة كلمة البحث
    }
    response = requests.get(search_url, headers=headers, params=params)
    print(response.json())
    return response.json()

# دالة لعرض الدورات
def display_courses(courses):
    for course in courses.get('results', []):
        insert_or_update_course(course)
        print(f"Course Name: {course.get('name')}")
        print(f"Course ID: {course.get('id')}")
        print(f"Start Date: {course.get('start')}")
        print("-" * 40)


# دالة لإدراج أو تحديث دورة

def insert_or_update_course(course_data):

    # البحث عن الدورة باستخدام course_id
    course = CoursesEdx.query.filter_by(course_id=course_data.get('id')).first()

    if course:
        # تحديث البيانات إذا كانت الدورة موجودة
        course.blocks_url = course_data.get('blocks_url')
        course.effort = course_data.get('effort')
        course.enrollment_start = course_data.get('enrollment_start')
        course.enrollment_end = course_data.get('enrollment_end')
        course.name = course_data.get('name')
        course.number = course_data.get('number')
        course.org = course_data.get('org')
        course.short_description = course_data.get('short_description')
        course.start = course_data.get('start')
        course.start_display = course_data.get('start_display')
        course.start_type = course_data.get('start_type')
        course.pacing = course_data.get('pacing')
        course.mobile_available = course_data.get('mobile_available', False)
        course.hidden = course_data.get('hidden', False)
        course.invitation_only = course_data.get('invitation_only', False)
        course.banner_image_url = course_data.get('media', {}).get('banner_image', {}).get('uri_absolute')
        course.course_image_url = course_data.get('media', {}).get('course_image', {}).get('uri')
        course.course_video_url = course_data.get('media', {}).get('course_video', {}).get('uri')
        print(f"تم تحديث الدورة: {course.name}")
    else:
        # إدراج دورة جديدة إذا لم تكن موجودة
        new_course = CoursesEdx(
            course_id=course_data.get('id'),
            blocks_url=course_data.get('blocks_url'),
            effort=course_data.get('effort'),
            enrollment_start=course_data.get('enrollment_start'),
            enrollment_end=course_data.get('enrollment_end'),
            name=course_data.get('name'),
            number=course_data.get('number'),
            org=course_data.get('org'),
            short_description=course_data.get('short_description'),
            start=course_data.get('start'),
            start_display=course_data.get('start_display'),
            start_type=course_data.get('start_type'),
            pacing=course_data.get('pacing'),
            mobile_available=course_data.get('mobile_available', False),
            hidden=course_data.get('hidden', False),
            invitation_only=course_data.get('invitation_only', False),
            banner_image_url=course_data.get('media', {}).get('banner_image', {}).get('uri_absolute'),
            course_image_url=course_data.get('media', {}).get('course_image', {}).get('uri'),
            course_video_url=course_data.get('media', {}).get('course_video', {}).get('uri')
        )
        db.session.add(new_course)
        print(f"تم إدراج الدورة: {new_course.name}")

    # حفظ التغييرات في قاعدة البيانات
    db.session.commit()
# الدالة الرئيسية
def getallcoursers():
    # الحصول على رمز الوصول
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        print("Failed to retrieve access token.")
        return

    # البحث عن دورات الجبر الخطي
    search_query = "Linear Algebra"
    courses_data = search_courses(access_token, "python")

    # عرض الدورات
    print(f"Found {len(courses_data.get('results', []))} courses related to '{search_query}':")
    display_courses(courses_data)



# with app.app_context():