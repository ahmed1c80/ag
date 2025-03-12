from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db import add_review,get_course_details,get_db_connection,has_reviewed 
from flask_bcrypt import Bcrypt
from models import db, User, Course, Enrollment
app = Flask(__name__)
bcrypt = Bcrypt(app)
def user_login():
       if request.method == 'POST':

        phone = request.form['phone']

        password = request.form['password']
        user = User.query.filter_by(phone=phone).first()
        
        #hashed_password = generate_password_hash(password)
        #print(bcrypt.check_password_hash(user.password_hash, password))
        #print(password)
		
        if user and bcrypt.check_password_hash(user.password_hash, password):#and check_password_hash(user.password_hash, hashed_password):
            login_user(user)
            return redirect(url_for('dashboard'))
			
            flash('User with this phone already exists!', 'danger')
       return render_template('login.html', title="Login")
       
def user_register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        phone = request.form['phone']
        password = request.form['password']
        gpa = request.form.get('gpa', type=float)
        major = request.form['major']
        #if not is_valid_phone(phone):
            #flash('Invalid phone number! Must be 9-15 digits.', 'danger')
            #return redirect(url_for('register'))
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            flash('User with this phone already exists!', 'danger')
            return redirect(url_for('register'))
        # تشفير كلمة المرور
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #hashed_password = generate_password_hash(password)
        new_user = User(full_name=full_name, phone=phone, password_hash=hashed_password, gpa=gpa, major=major)
        db.session.add(new_user)
        db.session.commit()
        flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')