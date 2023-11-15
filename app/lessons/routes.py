from flask import Blueprint, render_template, jsonify, request, session, current_app
from ..utils.functions import get_all_lessons, get_all_lesson_progress, get_lesson_by_id, get_recent_lessons, get_flashcards_by_lesson_id, get_lesson_by, get_user_content,login_required
from datetime import datetime as dt
from ..utils.database import get_db

lessons = Blueprint('lessons', __name__)

@lessons.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@lessons.route('/')
def index():
    lessons = get_all_lessons()
    progress = get_all_lesson_progress()

    return render_template('lessons.html', lessons=lessons, progress=progress)

@lessons.route('/<int:lesson_id>/<lesson_title>')
def flashcards_for_lessons(lesson_id,lesson_title):
    title = "Lesson | SpeakIT"
    lesson = get_lesson_by_id(lesson_id)
    user_id = session.get('user_id')
    flashcards = get_flashcards_by_lesson_id(lesson_id)
    progress = get_lesson_by(lesson_id)
    
    return render_template('flashcards.html', title=title, lesson=lesson, flashcards=flashcards, progress= progress,  user_id=user_id)

# def my_progress():
#     user_id = session.get('user_id')
#     db = get_db()
#     cur = db.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id,))
#     progress = cur.fetchall()

#     # Similarly, fetch flashcard access
#     cur = db.execute('SELECT * FROM user_flashcard_views WHERE user_id = ?', (user_id,))
#     flashcard_access = cur.fetchall()
#     # Then pass them to your template
#     return progress


@lessons.route('/access_flashcard/<int:flashcard_id>', methods=['POST'])
def access_flashcard(flashcard_id):
    user_id = session.get('user_id')
    if user_id is None:    
        db = get_db()
        db.execute('INSERT INTO user_flashcard_views (user_id, flashcard_id,  viewed) VALUES (?, ?, ?)',
                (user_id, flashcard_id, dt.now()))
        db.commit()
        return {'status': 'success'}, 200
    else:
        print("No user is logged in!")
        
#user progress
@lessons.route('/my_progress')
def my_progress():
    user_id = session.get('user_id')
    db = get_db()
    cur = db.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id,))
    lesson_progress = cur.fetchall()

    # Similarly, fetch flashcard access
    cur = db.execute('SELECT * FROM user_flashcard_views WHERE user_id = ?', (user_id,))
    flashcard_access = cur.fetchall()
    # Then pass them to your template
    return render_template('users.html', lesson_progress=lesson_progress, flashcard_access=flashcard_access)

#update user progress to the db
@lessons.route('/update_progress/<int:lesson_id>', methods=['POST'])
def update_progress(lesson_id):
    try:
        current_app.logger.info(f"Accessed blueprint: {request.blueprint}, route: {request.url_rule}")
        data = request.get_json()
        print(data)
        user_id = session.get('user_id')
        new_progress = data.get('progress')

        # Check the current progress
        conn = get_db()
        cursor = conn.cursor()

        current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                INSERT OR REPLACE INTO user_progress (user_id, lesson_id, progress, last_accessed)
                VALUES (?, ?, ?, ?)
            ''', (user_id, lesson_id, new_progress, current_time))

        conn.commit()

        return jsonify({'message': 'Progress updated successfully'}), 200
    except Exception as e:
        # If an error occurs, print it to the console and return a failure message
        print(e)
        return jsonify({'message': 'Failed to update progress'}), 500


user = Blueprint('user', __name__)

@user.route('/dashboard')
def dashboard():
    username = session.get('username')  # Retrieve the username from the Flask session
    lessons = get_recent_lessons()

    return render_template('user_dashboard.html', username=username, lessons = lessons)

@user.route('/my-learning')
def user_content():
    user_id = session.get('user_id')
    if user_id:    
        user_content = get_user_content(user_id)
        lessons = get_all_lessons()
        print(user_content)  # Add this line to debug
        return render_template('lesson_content.html', user_content = user_content, lessons=lessons)

@user.route('/all-lessons')
def all_lessons():
    user_id = session.get('user_id')    
    user_content = get_user_content(user_id)
    lessons = get_all_lessons()
    return render_template('lessons.html', user_content = user_content, lessons=lessons)

    