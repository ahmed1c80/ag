

# دالة لتحويل الدرجات إلى نقاط
def grade_to_gpa(grade):
    grade_map = {
        'A+': 5.0,
        'A': 4.75,
        'B+': 4.5,
        'B': 4.0,
        'C+': 3.5,
        'C': 3.0,
        'D+': 2.5,
        'D': 2.0,
        'F': 1.0
    }
    return grade_map.get(grade, 0.0)

# دالة لتحويل الدرجات إلى نقاط
def difficulty_to_val(diff):
    difficulty = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3
    }
    return difficulty.get(diff.lower(), 0)  # إرجاع None إذا لم يكن موجودًا

