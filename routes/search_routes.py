from flask import Blueprint, render_template, request, jsonify, send_file
from db.connection import execute_query
from flask_login import login_required
import pandas as pd
import io
from datetime import datetime

search_bp = Blueprint('search', __name__)

@search_bp.route('/')
@login_required
def search():
    barangays = execute_query("SELECT * FROM barangay ORDER BY name")
    return render_template('search.html', barangays=barangays)

@search_bp.route('/results')
@login_required
def search_results():
    # Get search parameters
    name = request.args.get('name', '')
    barangay_id = request.args.get('barangay_id', '')
    sitio_id = request.args.get('sitio_id', '')
    precinct = request.args.get('precinct', '')
    status = request.args.get('status', '')
    
    # Build query
    query = """
        SELECT v.*, b.name as barangay_name, s.name as sitio_name
        FROM voters v
        LEFT JOIN barangay b ON v.barangay_id = b.id
        LEFT JOIN sitio s ON v.sitio_id = s.id
        WHERE 1=1
    """
    params = {}
    
    if name:
        query += """ AND (
            v.last_name LIKE %(name)s OR
            v.first_name LIKE %(name)s OR
            v.middle_name LIKE %(name)s
        )"""
        params['name'] = f'%{name}%'
    
    if barangay_id:
        query += " AND v.barangay_id = %(barangay_id)s"
        params['barangay_id'] = barangay_id
    
    if sitio_id:
        query += " AND v.sitio_id = %(sitio_id)s"
        params['sitio_id'] = sitio_id
    
    if precinct:
        query += " AND v.precinct_number LIKE %(precinct)s"
        params['precinct'] = f'%{precinct}%'
    
    if status:
        query += " AND v.status = %(status)s"
        params['status'] = status
    
    query += " ORDER BY v.last_name, v.first_name"
    
    results = execute_query(query, params)
    return render_template('search_results.html', results=results)

@search_bp.route('/export')
@login_required
def export_results():
    # Get search parameters (same as search_results)
    name = request.args.get('name', '')
    barangay_id = request.args.get('barangay_id', '')
    sitio_id = request.args.get('sitio_id', '')
    precinct = request.args.get('precinct', '')
    status = request.args.get('status', '')
    
    # Build query (same as search_results)
    query = """
        SELECT 
            v.voter_id,
            v.last_name,
            v.first_name,
            v.middle_name,
            v.birth_date,
            v.gender,
            v.civil_status,
            v.address,
            b.name as barangay,
            s.name as sitio,
            v.precinct_number,
            v.contact_number,
            v.email,
            v.registration_date,
            v.status
        FROM voters v
        LEFT JOIN barangay b ON v.barangay_id = b.id
        LEFT JOIN sitio s ON v.sitio_id = s.id
        WHERE 1=1
    """
    params = {}
    
    if name:
        query += """ AND (
            v.last_name LIKE %(name)s OR
            v.first_name LIKE %(name)s OR
            v.middle_name LIKE %(name)s
        )"""
        params['name'] = f'%{name}%'
    
    if barangay_id:
        query += " AND v.barangay_id = %(barangay_id)s"
        params['barangay_id'] = barangay_id
    
    if sitio_id:
        query += " AND v.sitio_id = %(sitio_id)s"
        params['sitio_id'] = sitio_id
    
    if precinct:
        query += " AND v.precinct_number LIKE %(precinct)s"
        params['precinct'] = f'%{precinct}%'
    
    if status:
        query += " AND v.status = %(status)s"
        params['status'] = status
    
    query += " ORDER BY v.last_name, v.first_name"
    
    results = execute_query(query, params)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Voters')
    output.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'voter_records_{timestamp}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    ) 