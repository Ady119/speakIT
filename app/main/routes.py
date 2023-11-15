from flask import Blueprint, render_template
from ..utils.database import get_db
from ..utils.functions import get_recent_lessons
import sqlite3

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    title = "SpeakIT | Learning your way"    
    lessons = get_recent_lessons()
    
    return render_template('index.html', title=title, lessons=lessons)

# @main.route('/dashboard')
# def dashboard():
#     user_name = "Adrian L"  # Fetch from database/session
#     user_bio = "Enthusiastic language learner looking to improve"  # Fetch from database/session
#     user_courses = get_user_courses()  # You'll define this function to fetch course data
#     popular_flashcard_sets = get_popular_flashcard_sets()  # You'll define this function

#     return render_template('user_dashboard.html', 
#                             user_name=user_name, 
#                             user_bio=user_bio, 
#                             user_courses=user_courses,
#                             popular_flashcard_sets=popular_flashcard_sets)