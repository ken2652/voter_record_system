from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from db.connection import execute_query
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_voter():
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form.to_dict()
            photo = request.files.get('photo')
            
            # Handle photo upload if provided
            if photo:
                filename = secure_filename(f"{data['voter_id']}_{photo.filename}")
                photo_path = os.path.join('static', 'uploads', filename)
                photo.save(photo_path)
                data['photo_path'] = photo_path
            
            # Insert voter data
            query = """
                INSERT INTO voters (
                    voter_id, last_name, first_name, middle_name,
                    birth_date, gender, civil_status, address,
                    barangay_id, sitio_id, precinct_number,
                    contact_number, email, registration_date,
                    photo_path
                ) VALUES (
                    %(voter_id)s, %(last_name)s, %(first_name)s, %(middle_name)s,
                    %(birth_date)s, %(gender)s, %(civil_status)s, %(address)s,
                    %(barangay_id)s, %(sitio_id)s, %(precinct_number)s,
                    %(contact_number)s, %(email)s, %(registration_date)s,
                    %(photo_path)s
                )
            """
            execute_query(query, data)
            flash('Voter record added successfully!', 'success')
            return redirect(url_for('voter.view_voter', voter_id=data['voter_id']))
            
        except Exception as e:
            flash(f'Error adding voter record: {str(e)}', 'error')
            return redirect(url_for('voter.add_voter'))
    
    # GET request - show form
    barangays = execute_query("SELECT * FROM barangay ORDER BY name")
    return render_template('add_record.html', barangays=barangays)

@voter_bp.route('/edit/<voter_id>', methods=['GET', 'POST'])
@login_required
def edit_voter(voter_id):
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            data['voter_id'] = voter_id
            
            # Handle photo upload if provided
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo:
                    filename = secure_filename(f"{voter_id}_{photo.filename}")
                    photo_path = os.path.join('static', 'uploads', filename)
                    photo.save(photo_path)
                    data['photo_path'] = photo_path
            
            # Update voter data
            query = """
                UPDATE voters SET
                    last_name = %(last_name)s,
                    first_name = %(first_name)s,
                    middle_name = %(middle_name)s,
                    birth_date = %(birth_date)s,
                    gender = %(gender)s,
                    civil_status = %(civil_status)s,
                    address = %(address)s,
                    barangay_id = %(barangay_id)s,
                    sitio_id = %(sitio_id)s,
                    precinct_number = %(precinct_number)s,
                    contact_number = %(contact_number)s,
                    email = %(email)s,
                    status = %(status)s
                WHERE voter_id = %(voter_id)s
            """
            execute_query(query, data)
            flash('Voter record updated successfully!', 'success')
            return redirect(url_for('voter.view_voter', voter_id=voter_id))
            
        except Exception as e:
            flash(f'Error updating voter record: {str(e)}', 'error')
            return redirect(url_for('voter.edit_voter', voter_id=voter_id))
    
    # GET request - show form with existing data
    voter = execute_query(
        "SELECT * FROM voters WHERE voter_id = %s",
        (voter_id,)
    )[0]
    barangays = execute_query("SELECT * FROM barangay ORDER BY name")
    sitios = execute_query(
        "SELECT * FROM sitio WHERE barangay_id = %s ORDER BY name",
        (voter['barangay_id'],)
    )
    return render_template('edit_record.html',
                         voter=voter,
                         barangays=barangays,
                         sitios=sitios)

@voter_bp.route('/view/<voter_id>')
@login_required
def view_voter(voter_id):
    voter = execute_query("""
        SELECT v.*, b.name as barangay_name, s.name as sitio_name
        FROM voters v
        LEFT JOIN barangay b ON v.barangay_id = b.id
        LEFT JOIN sitio s ON v.sitio_id = s.id
        WHERE v.voter_id = %s
    """, (voter_id,))[0]
    return render_template('view_record.html', voter=voter)

@voter_bp.route('/delete/<voter_id>', methods=['POST'])
@login_required
def delete_voter(voter_id):
    try:
        execute_query("DELETE FROM voters WHERE voter_id = %s", (voter_id,))
        flash('Voter record deleted successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        flash(f'Error deleting voter record: {str(e)}', 'error')
        return redirect(url_for('voter.view_voter', voter_id=voter_id))

@voter_bp.route('/get_sitios/<int:barangay_id>')
def get_sitios(barangay_id):
    sitios = execute_query(
        "SELECT * FROM sitio WHERE barangay_id = %s ORDER BY name",
        (barangay_id,)
    )
    return jsonify(sitios)

@voter_bp.route('/barangay/<barangay>')
@login_required
def barangay_voters(barangay):
    query = """
    SELECT 
        NO,
        VOTERS_NAME,
        PRECINCT_NO,
        BARANGAY,
        SITIO,
        RICE_BENEFICIARY_1,
        RICE_BENEFICIARY_HEAD_2,
        BARANGAY_LEADER_3,
        LEVEL_1,
        LEVEL_2,
        LEVEL_3,
        REMARKS,
        RBH_NAME,
        BL_NAME
    FROM voters_record
    WHERE BARANGAY = %s
    ORDER BY NO
    """
    voters = execute_query(query, (barangay,))
    return render_template('voter/barangay_list.html', voters=voters, barangay=barangay) 