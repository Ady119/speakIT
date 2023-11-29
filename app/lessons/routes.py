from flask import Blueprint, render_template, jsonify, request, session, current_app, flash, redirect,  url_for
from ..utils.functions import get_all_lessons, get_all_lesson_progress, get_lesson_by_id, get_recent_lessons, get_flashcards_by_lesson_id, get_lesson_by, get_user_content,login_required, check_if_lessonTitle_exists, role_required, get_flashcard_count, allowed_file, get_flashcard_by_id, count_lessons, get_user_lessons_and_progress, count_completed_flashcards, get_last_access
from datetime import datetime as dt
from ..utils.database import get_db
import sqlite3
from ..admin.functions import update_lesson, get_lesson_by_title, delete_lessons
from werkzeug.utils import secure_filename
import os
lessons = Blueprint('lessons', __name__)

@lessons.route('/')
def index():
    title = "Lessons | SpeakIT"
    user_id = session.get('user_id')
    if user_id:
        user_content = get_user_content(user_id)
        lessons_progress = get_user_lessons_and_progress(user_id)
        return render_template('lessons.html', lessons=lessons_progress, user_content=user_content, user_id=user_id, lessons_progress= lessons_progress, title=title)
    else:
        lessons = get_all_lessons()
    return render_template('lessons.html', lessons=lessons, title=title)

#display flashcards for lesson in leaning mode
@lessons.route('/<int:lesson_id>/<lesson_title>')
@login_required
def flashcards_for_lessons(lesson_id,lesson_title):
    title = "<lesson_title> | SpeakIT"
    user_id = session.get('user_id')
    lesson = get_lesson_by_id(lesson_id)
    flashcards = get_flashcards_by_lesson_id(lesson_id)
    progress = get_lesson_by(lesson_id)
    user_content = get_user_content(user_id)
    return render_template('flashcards.html', title=title, lesson=lesson, flashcards=flashcards, progress= progress,  user_id=user_id)

@lessons.route('/access_flashcard/<int:flashcard_id>', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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

@lessons.route('/get_current_progress/<int:lesson_id>')
def get_current_progress(lesson_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'User not authenticated'}), 401
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT progress FROM user_progress WHERE user_id = ? AND lesson_id = ?''', (user_id, lesson_id))

        progress_row = cursor.fetchone()
        progress = progress_row[0] if progress_row else 0  # Default to 0 if no record found
        session['name']=progress
        return jsonify({"progress": progress})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to fetch progress'}), 500

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    title = "Dashboard| SpeakIT"
    username = session.get('username')  # Retrieve the username from the Flask session
    # lessons = get_recent_lessons()
    user_id = session.get('user_id')
    lessons = get_all_lessons()
    if user_id:
        user_content = get_user_content(user_id)
        lessons = get_all_lessons()
        count = count_lessons(user_id)
        pro = get_last_access(user_id)
        completed_flashcards = count_completed_flashcards(user_id)
        return render_template('user_dashboard.html', lessons=lessons, user_content=user_content, user_id=user_id, count=count, completed_flashcards=completed_flashcards, pro=pro, title=title)
    return render_template('lessons.html', lessons=lessons, title=title)

#displays lessons user started 
@user.route('/my-learning')
@login_required
def user_content():
    title = "My learning | SpeakIT"
    user_id = session.get('user_id')
    if user_id:    
        user_content = get_user_content(user_id)
        lessons = get_all_lessons()
        print(user_content)  # Add this line to debug
        return render_template('u-learning-content.html', user_content = user_content, lessons=lessons, title=title)

@lessons.route('/created-lessons', methods= ['GET'])
@login_required
def lessons_created():
    title = "Created Lessons | SpeakIT"
    user_id = session.get('user_id')
    
    if user_id and request.method == 'GET':
        lessons = get_all_lessons()
        
        return render_template('u-created-lessons.html', lessons= lessons, title=title)

#display flashcards, a lesson contains, listing them
@lessons.route('/lessons/content/<int:lesson_id>')
# @login_required
# @role_required('USER')
def lesson_flashcards(lesson_id):
    lesson = get_lesson_by_id(lesson_id)
    flashcards = get_flashcards_by_lesson_id(lesson_id)
    lesson_title = get_lesson_by_title(lesson_id)
    return render_template('a-lesson_content.html', lesson=lesson, lesson_id=lesson_id, flashcards= flashcards, lesson_title=lesson_title)

@user.route('/all-lessons')
def all_lessons():
    user_id = session.get('user_id')    
    user_content = get_user_content(user_id)
    lessons = get_all_lessons()
    
    return render_template('lessons.html', user_content = user_content, lessons=lessons)

@user.route('/create-lesson', methods=['GET', 'POST'])
def create_lesson():
    title = "Create lesson | SpeakIT"
    added_by = session.get('user_role')
    user_id = session.get('user_id')
    if user_id:
        if added_by == 'USER':
            if request.method == 'POST':
                added_by = session.get('user_role')
                lesson_title = request.form.get('lesson_title', '')
                lesson_desc = request.form.get('lesson_description', '')
                
                # Check if the title is empty
                if not lesson_title.strip():
                    flash('Lesson title is required!', 'error')
                    return render_template('u-add-lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)
                # Check if the title is empty
                if not lesson_desc.strip():
                    flash('Lesson description is required!', 'error')
                    return render_template('u-add-lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)
                
                # Check if the title already exists
                if check_if_lessonTitle_exists(lesson_title):
                    flash('Lesson title already exists!', 'error')
                    return render_template('u-add-lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)
                
                conn = get_db()
                cursor = conn.cursor()

                try:
                    created_at = dt.now()
                    cursor.execute("INSERT INTO lessons (lesson_title, lesson_description, created_at, added_by, user_id) VALUES (?, ?, ?, ?, ?)" 'RETURNING id', (lesson_title, lesson_desc, created_at, added_by, user_id))
                    new_lesson_id=cursor.fetchone() 
                    (inserted_id, ) = new_lesson_id if new_lesson_id else None
                    conn.commit()
                    lesson_id= inserted_id
                    print(inserted_id, )
                    flash("Lesson added successfully!", "success")
                except Exception as e:
                    flash(f"An error occurred while adding the lesson: {e}", "error")
                finally:
                    cursor.close()
                    conn.close()
            elif request.method =='GET':
                session.pop('_flashes', None)
                # Redirect to avoid form resubmission
                return render_template('u-add-lesson.html', title=title)

            # Render an empty form for GET requests
    return redirect(url_for('user.edit_lesson', lesson_id=lesson_id, lesson_title= lesson_title))

@user.route('/delete/lesson/<int:lesson_id>', methods=['POST'])
@login_required
@role_required('USER')
def delete_lesson(lesson_id):
    if request.method == 'POST':
        # Attempt to update the user, capture the result to check if it was successful
        delete_success = delete_lessons(lesson_id)
        
        if delete_success:
            flash('Flashcard deleted successfully!', 'success')
        else:
            flash('An error occurred while deleting the flashcard.', 'error')

    return redirect(url_for('user.all_lessons'))



@user.route('/lessons/edit_lesson/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
@role_required('USER')
def edit_lesson(lesson_id):
    lesson = get_lesson_by_id(lesson_id)
    flashcard_count = get_flashcard_count(lesson_id)
    if request.method == 'GET':
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = 'SELECT * FROM flashcards WHERE lesson_id = ?'
        cursor.execute(sql, (lesson_id,))
        flashcards = cursor.fetchall()
        
        return render_template('u-edit-lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count)
    
    elif request.method == 'POST':
        
        lesson_title = request.form.get('lesson_title', '')
        lesson_description = request.form.get('lesson_description', '')
        
        # Check if the title is empty
        if not lesson_title.strip():
            flash('Lesson title is required!', 'error')
            return render_template('u-edit-lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count)
        # Check if the title is empty
        if not lesson_description.strip():
            flash('Lesson description is required!', 'error')
            return render_template('u-edit-lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count)
        
        # Check if the title already exists
        if check_if_lessonTitle_exists(lesson_title):
            flash('Lesson title already exists!', 'error')
            return render_template('u-edit-lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count)
        
        lesson_title = request.form.get('lesson_title')
        lesson_description = request.form.get('lesson_description')
        
        # Connect to the database
        conn = get_db()
        cursor = conn.cursor()

        sql = """UPDATE lessons SET lesson_title = ?, lesson_description = ? WHERE id = ?"""
        cursor.execute(sql, (lesson_title, lesson_description, lesson_id))
        conn.commit()        
        
        flash(f"success")

        return render_template('u-edit-lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count)
    return redirect(url_for('user.edit_lesson', lesson_id=lesson_id))

@user.route('/lessons/add-flashcard/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
@role_required('USER')
def add_new_flashcard(lesson_id):
    lesson_title = get_lesson_by_title(lesson_id)
    added_by = session.get('user_role')
    flashcard_count = get_flashcard_count(lesson_id)

    if request.method == 'POST':
        content = request.form.get('content', '')
        translation = request.form.get('translation', '')
        example = request.form.get('example', '')
        # Check if the title is empty
        if not content.strip():
            flash('Content is required!', 'error')
            return render_template('u-add_flashcard.html', lesson_id= lesson_id, lesson_title=lesson_title, flashcard_count=flashcard_count)
        # Check if the title is empty
        if not translation.strip():
            flash('Translation is required!', 'error')
            return render_template('u-add_flashcard.html', lesson_id= lesson_id, lesson_title=lesson_title, flashcard_count=flashcard_count)
        print(lesson_title)
        filename = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):  # Implement allowed_file() to check file types
                    # Generate the upload path based on the lesson title
                lesson_upload_path = os.path.join(current_app.root_path, 'static', 'audio', lesson_title)
                os.makedirs(lesson_upload_path, exist_ok=True)
                filename = secure_filename(file.filename)
                filepath = os.path.join(lesson_upload_path, filename)
                file.save(filepath)

        try:
            conn = get_db()
            cursor = conn.cursor()
        
            # created_at = datetime.now()
            sql = "INSERT INTO flashcards (content, translation, example_sentence, lesson_id, audio_file_name, added_by) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (content, translation, example, lesson_id, filename, added_by))
            conn.commit()
            flash("Card added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred while adding the card: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    elif request.method =='GET':
        session.pop('_flashes', None)

        return render_template('u-add_flashcard.html', lesson_id= lesson_id, lesson_title=lesson_title, flashcard_count=flashcard_count)

    return redirect(url_for('lessons.lesson_flashcards', lesson_id=lesson_id))

@user.route('/flashcards/edit/<int:flashcard_id>/', methods=['GET', 'POST'])
@login_required
@role_required('USER')
def edit_flashcard(flashcard_id):
    flashcard = get_flashcard_by_id(flashcard_id)

    # Check if the flashcard data is valid
    if flashcard is None:
        flash("Flashcard not found", 'error')
        return redirect(request.referrer)

    # Fetch the lesson_id separately
    lesson_id = flashcard['lesson_id']
    # Fetch the lesson based on the lesson_id
    lesson = get_lesson_by_id(lesson_id)
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        content = request.form['flashcard_content']
        translation = request.form['flashcard_translation']
        example = request.form['example']
        filename = flashcard['audio_file_name'] 
        
        # Handle file upload
        file = request.files['flashcard_audio']

        if file and allowed_file(file.filename):
            # Generate subdirectory path based on lesson ID
            lesson_id = flashcard['lesson_id']
            lesson_title = get_lesson_by_title(lesson_id)
            
            # Generate the upload path based on the lesson title
            lesson_upload_path = os.path.join(current_app.root_path, 'static', 'audio', lesson_title)
            os.makedirs(lesson_upload_path, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(lesson_upload_path, filename)
            file.save(filepath)

        # Update the flashcard details in the database
        update_sql = """
        UPDATE flashcards
        SET content = ?, translation = ?, example_sentence = ?, audio_file_name = ?
        WHERE flashcard_id = ?
        """
        cursor.execute(update_sql, (content, translation, example, filename, flashcard_id,))
        db.commit()

        flash('Flashcard updated successfully!', 'success')
        return redirect(url_for('lessons.lesson_flashcards', lesson_id= lesson_id))


    return render_template('u-edit-flashcard.html', flashcard=flashcard, lesson=lesson)

@user.route('/delete/flashcard/<int:flashcard_id>', methods=['POST'])
@login_required
@role_required('USER')
def delete_flashcards(flashcard_id):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flashcards WHERE flashcard_id = ?", (flashcard_id,))
        conn.commit()
        lesson_id = request.form.get('lesson_id')
        
        flash('Flashcard deleted successfully!', 'success')
    except Exception as e:
        flash('An error occurred while deleting the flashcard.', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('lessons.lesson_flashcards', lesson_id=lesson_id))


@lessons.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
