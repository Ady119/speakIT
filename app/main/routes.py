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

@main.route('/speakIT/terms&conditions')
def terms():
    title = "SpeakIT | Terms & Conditions"    
    
    return render_template('privacy-policy.html', title=title)

@main.route('/speakIT/contactUs')
def contact():
    title = "SpeakIT | Contact Us"    
    
    return render_template('contact.html', title=title)
