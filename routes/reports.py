from flask import Blueprint, render_template, request, send_file
from db.connection import execute_query
from flask_login import login_required
import pandas as pd
import io
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def reports_dashboard():
    return render_template('reports/dashboard.html')

@reports_bp.route('/reports/barangay_summary')
@reports_bp.route('/reports/barangay_summary/<barangay>')
@login_required
def barangay_summary(barangay=None):
    if barangay:
        # Query for specific barangay voter list
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
        results = execute_query(query, (barangay,))
        return render_template('reports/barangay_list.html', voters=results, barangay=barangay)
    else:
        # Query for summary of all barangays
        query = """
        SELECT 
            BARANGAY,
            COUNT(*) as total_voters,
            SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
            SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rice_beneficiary_heads,
            SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as barangay_leaders,
            SUM(CASE WHEN LEVEL_1 = '1' THEN 1 ELSE 0 END) as level_1,
            SUM(CASE WHEN LEVEL_2 = '1' THEN 1 ELSE 0 END) as level_2,
            SUM(CASE WHEN LEVEL_3 = '1' THEN 1 ELSE 0 END) as level_3
        FROM voters_record
        GROUP BY BARANGAY
        ORDER BY BARANGAY
        """
        results = execute_query(query)
        return render_template('reports/barangay_summary.html', results=results)

@reports_bp.route('/reports/sitio_summary')
@login_required
def sitio_summary():
    query = """
    SELECT 
        BARANGAY,
        SITIO,
        COUNT(*) as total_voters,
        SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
        SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rice_beneficiary_heads,
        SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as barangay_leaders
    FROM voters_record
    GROUP BY BARANGAY, SITIO
    ORDER BY BARANGAY, SITIO
    """
    results = execute_query(query)
    return render_template('reports/sitio_summary.html', results=results)

@reports_bp.route('/reports/leader_analysis')
@login_required
def leader_analysis():
    query = """
    SELECT 
        r.*,
        COALESCE(rb.beneficiary_count, 0) as beneficiary_count,
        COALESCE(bl.leader_count, 0) as leader_count
    FROM (
        SELECT DISTINCT RBH_NAME, BL_NAME
        FROM voters_record
        WHERE RBH_NAME IS NOT NULL OR BL_NAME IS NOT NULL
    ) r
    LEFT JOIN (
        SELECT RBH_NAME, COUNT(*) as beneficiary_count
        FROM voters_record
        WHERE RICE_BENEFICIARY_1 = '1'
        GROUP BY RBH_NAME
    ) rb ON r.RBH_NAME = rb.RBH_NAME
    LEFT JOIN (
        SELECT BL_NAME, COUNT(*) as leader_count
        FROM voters_record
        WHERE BARANGAY_LEADER_3 = '1'
        GROUP BY BL_NAME
    ) bl ON r.BL_NAME = bl.BL_NAME
    ORDER BY beneficiary_count DESC, leader_count DESC
    """
    results = execute_query(query)
    return render_template('reports/leader_analysis.html', results=results)

@reports_bp.route('/reports/export/<report_type>')
@login_required
def export(report_type):
    if report_type == 'barangay_summary':
        query = """
        SELECT 
            BARANGAY,
            COUNT(*) as total_voters,
            SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
            SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rice_beneficiary_heads,
            SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as barangay_leaders,
            SUM(CASE WHEN LEVEL_1 = '1' THEN 1 ELSE 0 END) as level_1,
            SUM(CASE WHEN LEVEL_2 = '1' THEN 1 ELSE 0 END) as level_2,
            SUM(CASE WHEN LEVEL_3 = '1' THEN 1 ELSE 0 END) as level_3
        FROM voters_record
        GROUP BY BARANGAY
        ORDER BY BARANGAY
        """
        filename = 'barangay_summary'
    elif report_type == 'sitio_summary':
        query = """
        SELECT 
            BARANGAY,
            SITIO,
            COUNT(*) as total_voters,
            SUM(CASE WHEN RICE_BENEFICIARY_1 = '1' THEN 1 ELSE 0 END) as rice_beneficiaries,
            SUM(CASE WHEN RICE_BENEFICIARY_HEAD_2 = '1' THEN 1 ELSE 0 END) as rice_beneficiary_heads,
            SUM(CASE WHEN BARANGAY_LEADER_3 = '1' THEN 1 ELSE 0 END) as barangay_leaders
        FROM voters_record
        GROUP BY BARANGAY, SITIO
        ORDER BY BARANGAY, SITIO
        """
        filename = 'sitio_summary'
    elif report_type == 'leader_analysis':
        query = """
        SELECT 
            r.*,
            COALESCE(rb.beneficiary_count, 0) as beneficiary_count,
            COALESCE(bl.leader_count, 0) as leader_count
        FROM (
            SELECT DISTINCT RBH_NAME, BL_NAME
            FROM voters_record
            WHERE RBH_NAME IS NOT NULL OR BL_NAME IS NOT NULL
        ) r
        LEFT JOIN (
            SELECT RBH_NAME, COUNT(*) as beneficiary_count
            FROM voters_record
            WHERE RICE_BENEFICIARY_1 = '1'
            GROUP BY RBH_NAME
        ) rb ON r.RBH_NAME = rb.RBH_NAME
        LEFT JOIN (
            SELECT BL_NAME, COUNT(*) as leader_count
            FROM voters_record
            WHERE BARANGAY_LEADER_3 = '1'
            GROUP BY BL_NAME
        ) bl ON r.BL_NAME = bl.BL_NAME
        ORDER BY beneficiary_count DESC, leader_count DESC
        """
        filename = 'leader_analysis'
    else:
        return 'Invalid report type', 400

    results = execute_query(query)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    output.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    download_name = f'{filename}_{timestamp}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=download_name
    )

@reports_bp.route('/reports/charts/<chart_type>')
@login_required
def generate_chart(chart_type):
    if chart_type == 'barangay_distribution':
        query = """
        SELECT 
            BARANGAY,
            COUNT(*) as total_voters
        FROM voters_record
        GROUP BY BARANGAY
        ORDER BY total_voters DESC
        """
        results = execute_query(query)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='BARANGAY', y='total_voters')
        plt.xticks(rotation=45, ha='right')
        plt.title('Voter Distribution by Barangay')
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')
    
    return 'Invalid chart type', 400 