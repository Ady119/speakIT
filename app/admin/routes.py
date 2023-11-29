from flask import Blueprint, render_template, render_template, request, redirect, url_for,flash,session, current_app, render_template
from ..utils.functions import get_all_lessons, get_lesson_by_id, get_flashcard_by_id, check_if_lessonTitle_exists, get_users, get_user_by_id, login_required, role_required, get_flashcards_by_lesson_id, get_flashcard_count, count_all_lessons, count_all_users, count_all_cards, get_last_added_lesson, get_last_flashcard
from .functions import update_user, delete_user, update_lesson, get_upload_path, get_lesson_by_title, delete_lessons
from werkzeug.utils import secure_filename
from flask import *  
import sqlite3
from ..utils.database import get_db
from datetime import datetime
import os
from ..utils.functions import allowed_file
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
admin = Blueprint('admin', __name__)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/dashboard')
@login_required
@role_required('ADMIN')
def dashboard():
    title = "Admin Dashboard | SpeakIT"
    last_added_lesson = get_last_added_lesson()
    last_added_flashcard = get_last_flashcard()
    lessons_count = count_all_lessons()
    users_count = count_all_users()
    card_count = count_all_cards()
    return render_template('admin_dashboard.html', users=users, lessons_count=lessons_count, users_count=users_count, card_count=card_count, title=title, last_added_lesson=last_added_lesson, last_added_flashcard=last_added_flashcard)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/users', methods= ['GET', 'POST'])
@login_required
@role_required('ADMIN')
def users():
    title = "Users | SpeakIT"
    users = get_users()
    return render_template('a-users.html', users=users, title=title)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/users/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def edit_user(user_id):
    title = "Edit User | SpeakIT"
    if request.method == 'GET':
        user = get_user_by_id(user_id)
        print(f"GET Request: {user}")
        return render_template('edit_user.html', user=user, user_id=user_id, title=title)
    
    elif request.method == 'POST':
        updated_data = request.form

        # Attempt to update the user, capture the result to check if it was successful
        update_success = update_user(user_id, updated_data)

        return redirect(url_for('admin.users'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('ADMIN')
def delete_record(user_id):
    if request.method == 'POST':
        delete_success = delete_user(user_id)
        
        if delete_success:
            flash('User deleted successfully!', 'success')
        else:
            flash('An error occurred while deleting the user.', 'error')

        return redirect(url_for('admin.users'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/lessons')
@login_required
@role_required('ADMIN')
def lessons():
    title = "Lessons | SpeakIT"
    message = request.args.get('message', None)
    lessons = get_all_lessons()
    return render_template('a-lessons.html', lessons=lessons, message=message, title=title)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/lessons/<int:lesson_id>')
@login_required
@role_required('ADMIN')
def lesson_flashcards(lesson_id):
    title = "Lesson's content | SpeakIT"
    lesson = get_lesson_by_id(lesson_id)
    flashcards = get_flashcards_by_lesson_id(lesson_id)
    lesson_title = get_lesson_by_title(lesson_id)

    return render_template('a-lesson_content.html', lesson=lesson, lesson_id=lesson_id, flashcards= flashcards, lesson_title= lesson_title, title=title)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/lessons/add_lesson/', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def add_new_lesson():
    title = "Add Lesson | SpeakIT"
    if request.method == 'POST':
        lesson_title = request.form.get('lesson_title', '')
        lesson_desc = request.form.get('lesson_description', '')
        
        # Check if the title is empty
        if not lesson_title.strip():
            flash('Lesson title is required!', 'error')
            return render_template('add_lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)

        if not lesson_desc.strip():
            flash('Lesson description is required!', 'error')
            return render_template('add_lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)
        
        if check_if_lessonTitle_exists(lesson_title):
            flash('Lesson title already exists!', 'error')
            return render_template('add_lesson.html', lesson_title=lesson_title, lesson_desc=lesson_desc, title=title)
        
        conn = get_db()
        cursor = conn.cursor()

        try:
            created_at = datetime.now()
            cursor.execute("INSERT INTO lessons (lesson_title, lesson_description, created_at) VALUES (?, ?, ?)" 'RETURNING id', (lesson_title, lesson_desc, created_at))
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
        return render_template('add_lesson.html')

    return redirect(url_for('admin.edit_lesson', lesson_id=lesson_id, title=title))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/lessons/edit_lesson/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def edit_lesson(lesson_id):
    title = "Edit Lesson | SpeakIT"
    lesson = get_lesson_by_id(lesson_id)
    flashcard_count = get_flashcard_count(lesson_id)
    if request.method == 'GET':
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = 'SELECT * FROM flashcards WHERE lesson_id = ?'
        cursor.execute(sql, (lesson_id,))
        flashcards = cursor.fetchall()
        
        return render_template('edit_lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count, title=title)
    
    elif request.method == 'POST':
        lesson_title = request.form.get('lesson_title', '')
        lesson_description = request.form.get('lesson_description', '')
        
        # Check if the title is empty
        if not lesson_title.strip():
            flash('Lesson title is required!', 'error')
            return render_template('edit_lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count, title=title)

        if not lesson_description.strip():
            flash('Lesson description is required!', 'error')
            return render_template('edit_lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count, title=title)
        
        current_lesson_title = request.form.get('current_lesson_title', '')    
            
        if lesson_title != current_lesson_title:
            if check_if_lessonTitle_exists(lesson_title):
                flash('Lesson title already exists!', 'error')
                return render_template('edit_lesson.html', lesson=lesson, lesson_id=lesson_id, flashcard_count=flashcard_count, title=title)

        
        lesson_description = request.form.get('lesson_description')
        
        conn = get_db()
        cursor = conn.cursor()
        sql = """UPDATE lessons SET lesson_title = ?, lesson_description = ? WHERE id = ?"""

        # Execute the UPDATE statement with the updated data and user ID
        cursor.execute(sql, (lesson_title, lesson_description, lesson_id))
        conn.commit()        
        
        flash(f"success")

        return redirect(url_for('admin.edit_lesson', lesson_id=lesson_id, title=title))
    return redirect(url_for('admin.edit_lesson', title=title))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/flashcards/<int:lesson_id>', methods= ['GET'])
@login_required
@role_required('ADMIN')
def flashcards(lesson_id):
    title = "Flashcards | SpeakIT"
    message = request.args.get('message', None)
    flashcards = get_flashcards_by_lesson_id(lesson_id)
    lessons = get_all_lessons()
    lesson = get_lesson_by_id(lesson_id)

    return render_template('a-lesson_content.html', flashcards=flashcards, message=message, lessons=lessons, lesson= lesson, title=title) 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/delete/lesson/<int:lesson_id>', methods=['POST'])
@login_required
@role_required('ADMIN')
def delete_lesson(lesson_id):
    if request.method == 'POST':
        # Attempt to update the user, capture the result to check if it was successful
        delete_success = delete_lessons(lesson_id)
        
        if delete_success:
            flash('Flashcard deleted successfully!', 'success')
        else:
            flash('An error occurred while deleting the flashcard.', 'error')

    return redirect(url_for('admin.lessons'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.after_request
def add_headers(response):
    #required headers to the response
    return response
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/flashcards/edit/<int:flashcard_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def edit_flashcard(flashcard_id):
    title = "Edit Flashcard | SpeakIT"
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
        return redirect(url_for('admin.edit_flashcard',flashcard_id=flashcard_id, title=title))

    return render_template('edit_flashcards.html', flashcard=flashcard, lesson=lesson, title=title)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/delete/flashcard/<int:flashcard_id>', methods=['POST'])
@login_required
@role_required('ADMIN')
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
        # Handle the exception (e.g., logging)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('admin.lesson_flashcards', lesson_id=lesson_id))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.after_request
def add_headers(response):
    #required headers to the response
    return response
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@admin.route('/lessons/add-flashcard/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def add_new_flashcard(lesson_id):
    title = "Add Flashcard | SpeakIT"
    lesson_title = get_lesson_by_title(lesson_id)
    if request.method == 'POST':
        content = request.form.get('content', '')
        translation = request.form.get('translation', '')
        example = request.form.get('example', '')
        print(lesson_title)
        filename = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
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
            sql = "INSERT INTO flashcards (content, translation, example_sentence, lesson_id, audio_file_name) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (content, translation, example, lesson_id, filename))
            conn.commit()
            flash("Card added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred while adding the card: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    elif request.method =='GET':
        session.pop('_flashes', None)
        # Redirect to avoid form resubmission
        return render_template('add_fcard.html', lesson_id= lesson_id, title=title)

    # Render an empty form for GET requests
    return redirect(url_for('admin.lesson_flashcards', lesson_id=lesson_id, title=title))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
