from flask import request
from ..utils.database import get_db
from ..utils.functions import check_if_lessonTitle_exists
from flask import flash
from flask import Blueprint
from datetime import datetime
import os, sqlite3
from flask import current_app

def get_upload_path(lesson_title):
    # Define the base directory for audio uploads
    base_upload_dir = os.path.join(current_app.root_path, 'static', 'audio')

    # Create a subdirectory for each lesson based on lesson_title
    lesson_upload_dir = os.path.join(base_upload_dir, lesson_title)

    return lesson_upload_dir

    # return lesson  # This will return a tuple containing the lesson data or None if not found

# This function updates user data in the database
def update_user(user_id, updated_data):
    try:
        # Extract updated fields from the form data
        updated_username = updated_data.get('username')
        updated_email = updated_data.get('email')
        updated_password = updated_data.get('password')

        # Connect to the database
        conn = get_db()
        cursor = conn.cursor()

        # Construct an SQL UPDATE statement
        sql = """UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?"""

        # Execute the UPDATE statement with the updated data and user ID
        cursor.execute(sql, (updated_username, updated_email, updated_password, user_id))
        conn.commit()        
        
        flash(f"success")

    except Exception as e:
        # Handle exceptions, e.g., log the error or return an error response
        # flash('An error occurred while updating user information', 'error')
        flash(f"An error occurred: {str(e)}")
        return False
    finally:
        conn.close()
        
def delete_user(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        #SQL UPDATE statement
        sql = """DELETE FROM users WHERE id = ?"""
        # Execute the UPDATE statement where user ID
        cursor.execute(sql, (user_id,))
        conn.commit()        
        
        flash("User deleted successfully!", "success")
        return True

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")        
        return False
    finally:
        if conn:
            conn.close()
            


# This function updates user data in the database
def update_lesson(lesson_id, updated_data):
    try:
        # Extract updated fields from the form data
        updated_lesson_title = updated_data.get('lesson_title')
        updated_lesson_desc = updated_data.get('lesson_description')
        # updated_password = updated_data.get('password')

        # Connect to the database
        conn = get_db()
        cursor = conn.cursor()

        # Construct an SQL UPDATE statement
        sql = """UPDATE lessons SET lesson_title = ?, lesson_description = ? WHERE id = ?"""

        # Execute the UPDATE statement with the updated data and user ID
        cursor.execute(sql, (updated_lesson_title, updated_lesson_desc, lesson_id))
        conn.commit()        
        
    except Exception as e:
        # Handle exceptions, e.g., log the error or return an error response
        # flash('An error occurred while updating user information', 'error')
        flash(f"An error occurred: {str(e)}")
        return False
    finally:
        conn.close()

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

def update_flashcard(flashcard_id, content, translation, audio_file_name):
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    # Update SQL query with the correct parameters
    sql = """UPDATE flashcards SET content = ?, translation = ?, audio_file_name =? WHERE id = ?"""
    values = (content, translation, flashcard_id, audio_file_name)
    
    cursor.execute(sql, values)
    conn.commit()
    
    # Here you should return a value indicating success or failure
    return cursor.rowcount > 0

def delete_flashcard(flashcard_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        #SQL UPDATE statement
        sql = """DELETE FROM flashcards WHERE flashcard_id = ?"""
        # Execute the UPDATE statement where user ID
        cursor.execute(sql, (flashcard_id,))
        conn.commit()        
        
        flash("Flashcard deleted successfully!", "success")
        return True

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")        
        return False
    finally:
        if conn:
            conn.close()


def get_lesson_by_title(lesson_id):
    # Create a cursor object to interact with the database
    conn = get_db()
    cursor = conn.cursor()

    # Execute an SQL query to retrieve the lesson by title
    cursor.execute("SELECT lesson_title FROM lessons WHERE id = ?", (lesson_id,))
    
    # Fetch the lesson data
    lesson_title  = cursor.fetchone()

    return lesson_title[0]  # Return the lesson title as a string

