from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .database import get_db
from flask import session
import sqlite3

def get_users():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = ("""SELECT id, * FROM users""")
    cursor.execute(sql)
    users = cursor.fetchall()

    return users

def get_user_by_id(user_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = 'SELECT * FROM users WHERE id = ?'
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()  #fetchone row

    return user

def get_flashcards_by_lesson_id(lesson_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = 'SELECT * FROM flashcards WHERE lesson_id = ?'
    cursor.execute(sql, (lesson_id,))
    flashcards = cursor.fetchall()

    return flashcards

def get_flashcard_by_id(flashcard_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM flashcards WHERE flashcard_id = ?", (flashcard_id,))
    flashcard_data = cursor.fetchone()

    if flashcard_data:
        flashcard = {
            'flashcard_id': flashcard_data[0],
            'content': flashcard_data[1],
            'translation': flashcard_data[2],
            'example_sentence': flashcard_data[3],
            'lesson_id': flashcard_data[4],  # Include lesson_id in the dictionary
            'audio_file_name': flashcard_data[5]
        }
    else:
        flashcard = None  # Flashcard not found

    return flashcard

# Function to check if user exists
def check_if_lessonTitle_exists(lesson_title):
    conn = get_db()
    lesson_title = conn.execute('SELECT * FROM lessons WHERE lesson_title= ?', (lesson_title,)).fetchone()
    return lesson_title

def get_all_lessons():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = ("""SELECT id, lesson_title, lesson_description FROM lessons""")
    cursor.execute(sql)
    results = cursor.fetchall()

    return results 

def get_lesson_by_id(lesson_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM lessons WHERE id = ?'
    cursor.execute(sql, (lesson_id,))
    lesson = cursor.fetchone()  
    print("Lesson fetched:", lesson)  # Add this line for debugging
    return lesson

def get_lesson_by(lesson_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM user_progress WHERE lesson_id = ?'
    cursor.execute(sql, (lesson_id,))
    lesson = cursor.fetchone()  
    print("Lesson fetched:", lesson)  # Add this line for debugging
    return lesson

def get_all_lesson_progress():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM user_progress'
    cursor.execute(sql)
    progress = cursor.fetchall()  

    results = {}
    for row in progress:
        results[row['lesson_id']] = row['progress']
    
    return results

# def get_all_flashcards(lesson_id):
#     conn = get_db()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     sql = 'SELECT * FROM flashcards WHERE lesson_id = ?'
#     cursor.execute(sql, (lesson_id,))
#     flashcards = cursor.fetchall()

#     return flashcards

def get_all_flashcards():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = 'SELECT * from flashcards'
    cursor.execute(sql)
    
    flashcards = cursor.fetchall()
    
    return flashcards

def get_user_content(user_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = '''
        SELECT up.lesson_id, up.progress, up.last_accessed, l.lesson_title, l.lesson_description
        FROM user_progress up
        JOIN lessons l ON up.lesson_id = l.id
        WHERE up.user_id = ?
        ORDER BY up.last_accessed DESC
    ''' 
    cursor.execute(sql, (user_id,))
    
    user_content = cursor.fetchall()    
    return user_content

def get_flashcards_by_lesson_id(lesson_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = 'SELECT * FROM flashcards WHERE lesson_id = ?'
    cursor.execute(sql, (lesson_id,))
    flashcards = cursor.fetchall()

    return flashcards

def get_flashcard_by_id(flashcard_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = 'SELECT * FROM flashcards WHERE flashcard_id = ?'
    cursor.execute(sql, (flashcard_id,))
    flashcard = cursor.fetchone()
    return flashcard


# utils.py (create this file if it doesn't exist)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}  # Define the allowed file extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_recent_lessons(limit=3):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''SELECT * FROM lessons ORDER BY updated_at DESC LIMIT ?'''
    cursor.execute(sql, (limit,))
    lessons = cursor.fetchall()

    return lessons

# def get_flashcard_selection(limit=4):
#     conn = get_db()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
    
#     sql '''SELECT * FROM '''

# Function to check if user exists
def check_if_user_exists(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_authenticated' not in session:
            flash('You need to be logged in to view this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_role') != role:
                flash('You do not have the necessary permissions to view this page.', 'error')
                # return render_template('unauthorized.html'), 403  # Or redirect as needed
                return redirect(url_for('main.index'))  # Or wherever you want to redirect
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_flashcard_count(lesson_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM flashcards WHERE lesson_id= ?", (lesson_id,))
    flashcard_count = cursor.fetchone()[0]  # Fetches the first column of the first row
    cursor.close()
    conn.close()
    return flashcard_count
