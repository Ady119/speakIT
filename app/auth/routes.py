from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.database import get_db
from ..utils.functions import get_recent_lessons, get_user_content, get_all_lessons, check_if_user_exists, login_required, role_required
from datetime import datetime as dt

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    title = "Register | SpeakIT"
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Function to check if user exists
        if check_if_user_exists(username):
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))
            
        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
        (username, email, hashed_password))
        conn.commit()
        
        flash('Registered and logged in successfully!', 'success')
        return redirect(url_for('auth.login'))
    else:
        return render_template('register.html')
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    title = "Login | SpeakIT"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        user = '''SELECT * FROM users WHERE username = ?'''
        cursor.execute(user, (username,))
        result = cursor.fetchone()
        
        if result and check_password_hash(result['password'], password):
            session['user_authenticated'] = True
            session['user_role'] = result['role']
            session['username'] = result['username']
            session['user_id'] = result['id']
            print (session['user_id'])
            
            if result['role'] == "ADMIN":
                return redirect(url_for('admin.dashboard'))
            else:    
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login')) 
        
    return render_template('login.html', title = title)
        
@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_authenticated', None)
    
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))



