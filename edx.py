import requests

# Your credentials
client_id = '4XFPFh2yVUZLEcwZNYJXcoeOSD7Z297FAiakybUq'
client_secret = 'PB23HYz4qZUZJmtklsPbShLPN0C7tLHKhLCMsLCSkEB3Zjtb8HD0xXfdZM0temk0nIscg73CPg8VmHEWE7jxIzJATqsFn0zzL3rJg9KApWHmRd8LUYp84RK5lBOEmaFy'
token_url = 'https://courses.edx.org/oauth2/access_token'

# Step 1: Authenticate and Get Access Token
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

# Step 2: Fetch Courses from the edX API
def get_all_courses(courses_url, headers):
    all_courses = []
    #while courses_url:
    response = requests.get(courses_url, headers=headers)
    print(response.json())
    data = response.json()
    all_courses.extend(data.get('results', []))
    courses_url = data.get('pagination', {}).get('next')
    return all_courses

# Step 3: Process and Display Course Data
def display_courses(courses):
    for course in courses:
        print(f"Course Name: {course.get('name')}")
        print(f"Course ID: {course.get('id')}")
        print(f"Start Date: {course.get('start')}")
        print("-" * 40)

# Main Function
def main():
    # Get Access Token
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        print("Failed to retrieve access token.")
        return

    print("Access Token:", access_token)

    # API endpoint for fetching courses
    courses_url = 'https://courses.edx.org/api/courses/v1/courses/?page_size=1'
    #courses_url='https://api.edx.org/catalog/v1/catalogs/1/courses'
    headers = {
        'Authorization': f'JWT {access_token}',
        'Accept': 'application/json'
    }

    # Fetch All Courses
    all_courses = get_all_courses(courses_url, headers)
    print("Total Courses:", len(all_courses))

    # Display Courses
    display_courses(all_courses)

if __name__ == "__main__":
    main()