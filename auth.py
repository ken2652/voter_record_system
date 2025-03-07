from flask_login import LoginManager, UserMixin
from functools import wraps
from flask import current_app, redirect, url_for, flash, session

# User class
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.role = user_data['role']
        self._is_active = user_data['is_active']

    @property
    def is_active(self):
        return bool(self._is_active)
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = bool(value)

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app import get_db_connection
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                if user_data:
                    return User(user_data)
            except Exception as e:
                print(f"Error loading user: {e}")
        return None 