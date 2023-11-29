from flask import Flask, session
from flask_session import Session
from error_handler import error as error_blueprint
from main.routes import main as main_blueprint
from auth.routes import auth as auth_blueprint
from lessons.routes import user as user_blueprint
from admin.routes import admin as admin_blueprint
from lessons.routes import lessons as lessons_blueprint
from utils.database import init_app as init_app
import os
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # filesystem for storing session data
app.config['SESSION_PERMANENT'] = False  # Session will not expire when the browser is closed
# app.config['SESSION_USE_SIGNER'] = True  # Sign session cookies for security
app.config['SESSION_KEY_PREFIX'] = 'session:'  # Prefix for session keys
app.config['SESSION_COOKIE_NAME'] = 'app_session'  # Name of the session cookie

    # Initialize Flask-Session
Session(app)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')
app.secret_key = 'd@joa&da1Tg1sfj031823e0dk(*&^D)'
app.config.from_object('config.Config')
app.config['DATABASE'] = os.path.join(basedir, 'database', 'speak_it.db')
    
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'audio')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
init_app(app)
    #blueprint registration>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
app.register_blueprint(main_blueprint, url_prefix='/')
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(lessons_blueprint, url_prefix='/lessons')
app.register_blueprint(error_blueprint)
    
if __name__ == '__main__':
    app.run(debug=True)
