
# ✅ API لاسترجاع الدورات الموصى بها بناءً على المعدل التراكمي
@app.route('/api/recommend_coursesp', methods=['GET'])
def recommend_coursesp():
    if current_user.id==0:
        return jsonify({"error": "User not logged in"}), 401

    student_id = current_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 استرجاع معدل الطالب التراكمي
    cursor.execute("SELECT gpa FROM users WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    student_gpa = student['gpa']

    # 🔹 استرجاع الدورات المناسبة بناءً على المعدل التراكمي
    cursor.execute("""
        SELECT *
        FROM courses
        WHERE gpa_requirement <= %s
        ORDER BY gpa_requirement desc
    """, (student_gpa,))

    recommendations = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(recommendations)
	
