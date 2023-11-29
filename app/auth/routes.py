from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.database import get_db
from ..utils.functions import  check_if_user_exists, login_required, role_required, get_user_by_id, get_user_by_username, update_email, update_password, update_username, get_user_info
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
        current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password, member_since) VALUES (?, ?, ?, ?)', 
        (username, email, hashed_password, current_time))
        conn.commit()
        
        flash('Congratulations, registration complete!', 'success')
        return redirect(url_for('auth.login'))
    else:
        return render_template('register.html', title=title)
    
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
            session['email'] = result['email']

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
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_authenticated', None)
    
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/profile/settings', methods = ['GET'])
@login_required
def profile():
    user_id = session.get('user_id')
    title = "Profile Settings | SpeakIT"
    users = get_user_info(user_id)
    return render_template('u-profile.html', username=session.get('username'), email=session.get('email'), title=title, users= users)

@auth.route('/update', methods=['POST'])
@login_required
def update_profile():
    title = "Profile settings | SpeakIT"
    user_id = session.get('user_id')

    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    new_username = request.form.get('new_username', '').strip()
    new_email = request.form.get('new_email', '').strip()

    if new_password and old_password:
        user = get_user_by_id(user_id)
        if check_password_hash(user['password'], old_password):
            new_password_hash = generate_password_hash(new_password)
            update_password(user_id, new_password_hash)
            flash('Password successfully updated.')
        else:
            flash('Old password is incorrect.')

    if new_username:
        if check_if_user_exists(new_username):
            flash('Username already exists!', 'error')
        else:
            update_username(user_id, new_username)
            session['username'] = new_username
            flash('Username updated!', 'success')

    if new_email:
        update_email(user_id, new_email)
        session['email'] = new_email
        flash('Email updated!', 'success')

    return redirect(url_for('auth.profile', title=title))


