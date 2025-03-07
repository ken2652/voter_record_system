from flask import Blueprint, render_template, request
from db.connection import execute_query
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get total voters count
    total_voters = execute_query("SELECT COUNT(*) as count FROM voters")[0]['count']
    
    # Get active voters count
    active_voters = execute_query(
        "SELECT COUNT(*) as count FROM voters WHERE status = 'Active'"
    )[0]['count']
    
    # Get voters by barangay
    voters_by_barangay = execute_query("""
        SELECT b.name, COUNT(v.id) as count 
        FROM barangay b 
        LEFT JOIN voters v ON b.id = v.barangay_id 
        GROUP BY b.id, b.name
    """)
    
    # Get recent registrations
    recent_registrations = execute_query("""
        SELECT v.*, b.name as barangay_name, s.name as sitio_name 
        FROM voters v 
        LEFT JOIN barangay b ON v.barangay_id = b.id 
        LEFT JOIN sitio s ON v.sitio_id = s.id 
        ORDER BY v.created_at DESC 
        LIMIT 5
    """)
    
    return render_template('index.html',
                         total_voters=total_voters,
                         active_voters=active_voters,
                         voters_by_barangay=voters_by_barangay,
                         recent_registrations=recent_registrations) 