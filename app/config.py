import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE = 'database/speak_it.db'
