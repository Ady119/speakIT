from ..utils.database import get_db
from flask import flash
import os
from flask import current_app
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_upload_path(lesson_title):
    # Define the base directory for audio uploads
    base_upload_dir = os.path.join(current_app.root_path, 'static', 'audio')
    # Create a subdirectory for each lesson based on lesson_title
    lesson_upload_dir = os.path.join(base_upload_dir, lesson_title)

    return lesson_upload_dir
# updates user data in the database>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def update_user(user_id, updated_data):
    try:
        updated_username = updated_data.get('username')
        updated_email = updated_data.get('email')
        updated_password = updated_data.get('password')

        conn = get_db()
        cursor = conn.cursor()

        sql = """UPDATE users SET username = ?, email = ? WHERE id = ?"""
        cursor.execute(sql, (updated_username, updated_email, user_id))
        conn.commit()        
        
        flash("User detail updated!" , "success")

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return False
    finally:
        conn.close()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def delete_user(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        #SQL UPDATE statement
        sql = """DELETE FROM users WHERE id = ?"""
        # Execute the UPDATE statement where user ID
        cursor.execute(sql, (user_id,))
        conn.commit()        
        
        return True

    except Exception as e:
        return False
    finally:
        if conn:
            conn.close()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# This function updates user data in the database
def update_lesson(lesson_id, updated_data):
    try:
        # Extract updated fields from the form data
        updated_lesson_title = updated_data.get('lesson_title')
        updated_lesson_desc = updated_data.get('lesson_description')

        # Connect to the database
        conn = get_db()
        cursor = conn.cursor()

        sql = """UPDATE lessons SET lesson_title = ?, lesson_description = ? WHERE id = ?"""
        cursor.execute(sql, (updated_lesson_title, updated_lesson_desc, lesson_id))
        conn.commit()        
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return False
    finally:
        conn.close()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def delete_lessons(lesson_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        #SQL UPDATE statement
        sql = """DELETE FROM lessons WHERE id = ?"""
        # Execute the UPDATE statement where user ID
        cursor.execute(sql, (lesson_id,))
        conn.commit()        
        
        flash("Lesson deleted successfully!", "success")
        return True

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")        
        return False
    finally:
        if conn:
            conn.close()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def update_flashcard(flashcard_id, content, translation, audio_file_name):
    conn = get_db()
    cursor = conn.cursor()

    sql = """UPDATE flashcards SET content = ?, translation = ?, audio_file_name =? WHERE id = ?"""
    values = (content, translation, flashcard_id, audio_file_name)
    cursor.execute(sql, values)
    conn.commit()
    
    return cursor.rowcount > 0
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_lesson_by_title(lesson_id):
    # Create a cursor object to interact with the database
    conn = get_db()
    cursor = conn.cursor()
    # Execute an SQL query to retrieve the lesson by title
    cursor.execute("SELECT lesson_title FROM lessons WHERE id = ?", (lesson_id,))

    # Fetch the lesson data
    lesson_title  = cursor.fetchone()

    return lesson_title[0]  # Return the lesson title as a string

