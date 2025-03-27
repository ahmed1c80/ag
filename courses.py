from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy




@app.route('/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        new_course = Course(
            course_name=request.form['course_name'],
            course_code=request.form['course_code'],
            description=request.form['description'],
            instructor=request.form['instructor'],
            credits=int(request.form['credits']),
            university=request.form['university'],
            difficulty_level=request.form['difficulty_level'],
            prerequisites=request.form['prerequisites'],
            gpa_requirement=float(request.form['gpa_requirement']) if request.form['gpa_requirement'] else None,
            language=request.form['language'],
            course_link=request.form['course_link'],
            category=request.form['category']
        )
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('view_courses'))
    return render_template('add_course.html')



