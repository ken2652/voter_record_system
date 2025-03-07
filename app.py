from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import traceback
import sys
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import random
import string
from routes.reports import reports_bp
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import init_login_manager, User

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize Flask-Login
init_login_manager(app)

# Register blueprints
app.register_blueprint(reports_bp)

def get_avatar_url(email):
    """Generate a random avatar URL using Gravatar's default random avatars"""
    email = email.lower().encode('utf-8')
    gravatar_hash = hashlib.md5(email).hexdigest()
    return f"https://www.gravatar.com/avatar/{gravatar_hash}?d=identicon&s=200"

# Make the function available in templates
app.jinja_env.globals.update(get_avatar_url=get_avatar_url)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Test@123',
    'database': 'voter_records'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                user_data = cursor.fetchone()
                
                if user_data and check_password_hash(user_data['password_hash'], password):
                    user = User(user_data)
                    login_user(user)
                    session['user_id'] = user_data['id']
                    session['username'] = user_data['username']
                    session['role'] = user_data['role']
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password.', 'danger')
            except Error as e:
                flash(f'Database error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form['role']
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                hashed_password = generate_password_hash(password)
                # Generate a default email using username
                default_email = f"{username}@roxascity.gov.ph"
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, full_name, role)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (username, hashed_password, default_email, full_name, role))
                conn.commit()
                flash('User registered successfully!', 'success')
                return redirect(url_for('manage_users'))
            except Error as e:
                flash(f'Error registering user: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
    return render_template('register.html')

@app.route('/manage_users')
@admin_required
def manage_users():
    conn = get_db_connection()
    users = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT id, username, email, role, is_active, created_at FROM users')
            users = cursor.fetchall()
            cursor.close()
        except Error as e:
            flash(f'Error fetching users: {str(e)}', 'danger')
        finally:
            conn.close()
    return render_template('manage_users.html', users=users)

@app.route('/')
@login_required
def index():
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Unable to connect to database.', 'danger')
            return render_template('errors/500.html'), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Get all records
        cursor.execute('SELECT * FROM voters_record')
        all_records = cursor.fetchall()
        
        # Get records grouped by barangay
        cursor.execute('''
            SELECT 
                BARANGAY,
                COUNT(*) as total_voters,
                SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
                SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rbh_count,
                SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as bl_count
            FROM voters_record 
            GROUP BY BARANGAY
        ''')
        barangay_stats = cursor.fetchall()
        
        # Convert to dictionary for easy access
        barangay_stats_dict = {stat['BARANGAY']: stat for stat in barangay_stats}
        
        cursor.close()
        conn.close()
        
        # List of all barangays
        barangays = [
            "ADLAWAN", "BAGO", "BALIJUAGAN", "BANICA", "BARRA", "BATO", "BAYBAY", "BOLO",
            "CABUGAO", "CAGAY", "COGON", "CULAJAO", "CULASI", "DAYAO", "DINGINAN", "DUMOLOG",
            "GABU-AN", "INZO ARNALDO VILLAGE", "JUMAGUICJIC", "LANOT", "LAWA-AN", "LIBAS",
            "LIONG", "LOCTUGAN", "LONOY", "MILIBILI", "MONGPONG", "OLOTAYAN", "POB I",
            "POB II", "POB III", "POB IV", "POB V", "POB VI", "POB VII", "POB VIII",
            "POB IX", "POB X", "POB XI", "PUNTA COGON", "PUNTA TABUC", "SAN JOSE",
            "SIBAGUAN", "TALON", "TANQUE", "TANZA", "TIZA"
        ]
        
        # Initialize stats for barangays with no records
        for barangay in barangays:
            if barangay not in barangay_stats_dict:
                barangay_stats_dict[barangay] = {
                    'BARANGAY': barangay,
                    'total_voters': 0,
                    'rice_beneficiaries': 0,
                    'rbh_count': 0,
                    'bl_count': 0
                }
        
        return render_template('index.html', 
                             records=all_records, 
                             barangay_stats=barangay_stats_dict,
                             barangays=barangays)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('errors/500.html'), 500

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            if conn is None:
                flash('Unable to connect to database. Please check your database configuration.', 'danger')
                return render_template('errors/500.html'), 500

            cursor = conn.cursor()
            # Set the user_id for the trigger
            cursor.execute('SET @user_id = %s', (session.get('user_id'),))
            
            # Get form data
            voters_name = request.form['voters_name']
            precinct_no = request.form['precinct_no']
            barangay = request.form['barangay']
            sitio = request.form['sitio']
            rice_beneficiary_1 = request.form.get('rice_beneficiary_1', None)
            rice_beneficiary_head_2 = request.form.get('rice_beneficiary_head_2', None)
            barangay_leader_3 = request.form.get('barangay_leader_3', None)
            level_1 = request.form.get('level_1', None)
            level_2 = request.form.get('level_2', None)
            level_3 = request.form.get('level_3', None)
            remarks = request.form['remarks']
            rbh_name = request.form['rbh_name']
            bl_name = request.form['bl_name']

            cursor.execute('''
                INSERT INTO voters_record (
                    VOTERS_NAME, PRECINCT_NO, BARANGAY, SITIO,
                    RICE_BENEFICIARY_1, RICE_BENEFICIARY_HEAD_2, BARANGAY_LEADER_3,
                    LEVEL_1, LEVEL_2, LEVEL_3, REMARKS, RBH_NAME, BL_NAME
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                voters_name, precinct_no, barangay, sitio,
                '1' if rice_beneficiary_1 else None,
                '1' if rice_beneficiary_head_2 else None,
                '1' if barangay_leader_3 else None,
                '1' if level_1 else None,
                '1' if level_2 else None,
                '1' if level_3 else None,
                remarks, rbh_name, bl_name
            ))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Record added successfully!', 'success')
            return redirect(url_for('index'))
        except Error as e:
            flash(f'Database error: {str(e)}', 'danger')
            return render_template('errors/500.html'), 500
    return render_template('add_record.html')

@app.route('/edit_record/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Unable to connect to database. Please check your database configuration.', 'danger')
            return render_template('errors/500.html'), 500

        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            try:
                # Set the user_id for the trigger
                cursor.execute('SET @user_id = %s', (session.get('user_id'),))
                
                cursor.execute('''
                    UPDATE voters_record SET
                        VOTERS_NAME = %s,
                        PRECINCT_NO = %s,
                        BARANGAY = %s,
                        SITIO = %s,
                        RICE_BENEFICIARY_1 = %s,
                        RICE_BENEFICIARY_HEAD_2 = %s,
                        BARANGAY_LEADER_3 = %s,
                        LEVEL_1 = %s,
                        LEVEL_2 = %s,
                        LEVEL_3 = %s,
                        REMARKS = %s,
                        RBH_NAME = %s,
                        BL_NAME = %s
                    WHERE NO = %s
                ''', (
                    request.form['voters_name'],
                    request.form['precinct_no'],
                    request.form['barangay'],
                    request.form['sitio'],
                    '1' if request.form.get('rice_beneficiary_1') else None,
                    '1' if request.form.get('rice_beneficiary_head_2') else None,
                    '1' if request.form.get('barangay_leader_3') else None,
                    '1' if request.form.get('level_1') else None,
                    '1' if request.form.get('level_2') else None,
                    '1' if request.form.get('level_3') else None,
                    request.form['remarks'],
                    request.form['rbh_name'],
                    request.form['bl_name'],
                    id
                ))
                conn.commit()
                flash('Record updated successfully!', 'success')
                return redirect(url_for('index'))
            except Error as e:
                flash(f'Error updating record: {str(e)}', 'danger')
                return render_template('errors/500.html'), 500
        
        # Get record for editing
        cursor.execute('SELECT * FROM voters_record WHERE NO = %s', (id,))
        record = cursor.fetchone()
        if record is None:
            flash('Record not found.', 'danger')
            return redirect(url_for('index'))
        
        cursor.close()
        conn.close()
        return render_template('edit_record.html', record=record)
    except Error as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('errors/500.html'), 500

@app.route('/delete_record/<int:id>')
def delete_record(id):
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Unable to connect to database. Please check your database configuration.', 'danger')
            return render_template('errors/500.html'), 500
            
        cursor = conn.cursor()
        # Set the user_id for the trigger
        cursor.execute('SET @user_id = %s', (session.get('user_id'),))
        
        cursor.execute('DELETE FROM voters_record WHERE NO = %s', (id,))
        conn.commit()
        
        # Reset record numbers after deletion
        cursor.execute('CALL reset_record_numbers()')
        conn.commit()
        
        cursor.close()
        conn.close()
        flash('Record deleted successfully!', 'success')
        return redirect(url_for('index'))
    except Error as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('errors/500.html'), 500

@app.route('/edit_user/<int:user_id>')
@login_required
def edit_user(user_id):
    if not session.get('role') == 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return redirect(url_for('manage_users'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('manage_users'))
            
        return render_template('edit_user.html', user=user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('manage_users'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not session.get('role') == 'admin':
        return jsonify({'success': False, 'message': 'Access denied. Admin privileges required.'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error.'})
        
    try:
        cursor = conn.cursor()
        # Check if user exists and is not the current user
        cursor.execute('SELECT username FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'})
        
        if user[0] == session.get('username'):
            return jsonify({'success': False, 'message': 'Cannot delete your own account.'})
        
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not session.get('role') == 'admin':
        return jsonify({'success': False, 'message': 'Access denied. Admin privileges required.'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error.'})
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT username FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'})
        
        # Get password from request
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'success': False, 'message': 'No password provided'})
            
        new_password = data['password']
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'})
            
        hashed_password = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (hashed_password, user_id))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Add the edit_user POST route
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user_post(user_id):
    if not session.get('role') == 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return redirect(url_for('manage_users'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            role = request.form['role']
            is_active = 1 if request.form.get('is_active') else 0
            
            # Check if username already exists for other users
            cursor.execute('SELECT id FROM users WHERE username = %s AND id != %s', (username, user_id))
            if cursor.fetchone():
                flash('Username already exists.', 'danger')
                return redirect(url_for('edit_user', user_id=user_id))
            
            cursor.execute('''
                UPDATE users 
                SET username = %s, email = %s, role = %s, is_active = %s 
                WHERE id = %s
            ''', (username, email, role, is_active, user_id))
            conn.commit()
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('manage_users'))
            
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('manage_users'))
            
        return render_template('edit_user.html', user=user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('manage_users'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_barangay_records/<barangay>')
@login_required
def get_barangay_records(barangay):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM voters_record WHERE BARANGAY = %s', (barangay,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_barangay_stats/<barangay>')
@login_required
def get_barangay_stats(barangay):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                COUNT(*) as total_voters,
                SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
                SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rbh_count,
                SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as bl_count
            FROM voters_record 
            WHERE BARANGAY = %s
        ''', (barangay,))
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit_history')
@login_required
@admin_required  # Add this decorator
def edit_history():
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Unable to connect to database.', 'danger')
            return render_template('errors/500.html'), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Admin sees all records
        cursor.execute('''
            SELECT 
                vh.*,
                u.username as modified_by
            FROM voters_record_history vh
            LEFT JOIN users u ON vh.user_id = u.id
            ORDER BY vh.modified_at DESC
            LIMIT 100
        ''')
            
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('edit_history.html', history=history)
    except Exception as e:
        flash(f'Error fetching edit history: {str(e)}', 'danger')
        return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    error_msg = str(error)
    if hasattr(error, '__cause__') and error.__cause__:
        error_msg += f'\nCaused by: {str(error.__cause__)}'
    print(f"500 Error: {error_msg}\n{traceback.format_exc()}")
    return render_template('errors/500.html', error=error_msg), 500

if __name__ == '__main__':
    app.run(debug=True)