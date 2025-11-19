"""
Hostel Maintenance System - Flask Backend with Firebase Authentication
Supports Admin/Warden and Student/Resident roles
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, db
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here-change-in-production')
CORS(app)

# ==================== FIREBASE INITIALIZATION ====================
# Initialize Firebase Admin SDK
try:
    # Load Firebase credentials from environment or file
    firebase_creds_path = os.getenv('FIREBASE_CREDS_PATH', 'firebase-adminsdk.json')
    
    if os.path.exists(firebase_creds_path):
        cred = credentials.Certificate(firebase_creds_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    else:
        print("⚠️ Firebase credentials file not found. Firebase features will be unavailable.")
except Exception as e:
    print(f"❌ Firebase initialization error: {str(e)}")

# MySQL Configuration
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'homelike')
}

def get_db_connection():
    """Establish MySQL database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def get_user_role(user_email):
    """
    Determine user role (Admin/Warden or Student/Resident) based on email.
    Returns tuple: (role, user_data)
    """
    conn = get_db_connection()
    if not conn:
        return None, None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user is a Warden
        cursor.execute("SELECT * FROM Warden WHERE Wmail = %s", (user_email,))
        warden = cursor.fetchone()
        if warden:
            cursor.close()
            conn.close()
            return 'warden', warden
        
        # Check if user is a Student
        cursor.execute("SELECT * FROM Student WHERE Smail = %s", (user_email,))
        student = cursor.fetchone()
        if student:
            cursor.close()
            conn.close()
            return 'student', student
        
    finally:
        cursor.close()
        conn.close()
    
    return None, None

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login page with Firebase authentication."""
    firebase_config = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID'),
    }
    return render_template('login_firebase.html', firebase_config=json.dumps(firebase_config))

@app.route('/api/auth/firebase', methods=['POST'])
def firebase_auth():
    """
    Handle Firebase token verification on backend.
    Frontend sends ID token after Firebase authentication.
    """
    try:
        data = request.json
        id_token_str = data.get('idToken')
        
        if not id_token_str:
            return jsonify({'error': 'No token provided'}), 400
        
        # Verify Firebase ID token
        try:
            decoded_token = auth.verify_id_token(id_token_str)
            user_email = decoded_token.get('email')
            user_name = decoded_token.get('name', 'User')
            user_uid = decoded_token.get('uid')
            
            # Determine user role from database
            role, user_data = get_user_role(user_email)
            
            if not role:
                return jsonify({
                    'error': 'User not registered in the system. Please contact administration.'
                }), 401
            
            # Store in session
            session['user'] = {
                'uid': user_uid,
                'email': user_email,
                'name': user_name,
                'role': role,
                'id': user_data['WardenID'] if role == 'warden' else user_data['SId'],
                'hostel_id': user_data['HId']
            }
            session.permanent = True
            
            return jsonify({
                'success': True,
                'role': role,
                'redirect': url_for('dashboard')
            }), 200
            
        except auth.InvalidIdTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except auth.ExpiredIdTokenError:
            return jsonify({'error': 'Token expired'}), 401
            
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/dashboard')
def dashboard():
    """Main dashboard - routed based on user role."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] == 'warden':
        return render_template('warden_dashboard.html', user=user)
    else:
        return render_template('student_dashboard.html', user=user)

@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('login'))

# ==================== STUDENT API ENDPOINTS ====================

@app.route('/api/student/file-complaint', methods=['POST'])
def file_complaint():
    """
    Student files a new complaint.
    Required: description, complaint_type (Room, Washroom, Filter), amenity_id
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        student_id = session['user']['id']
        hostel_id = session['user']['hostel_id']
        
        description = data.get('description', '').strip()
        complaint_type = data.get('complaint_type', '').strip()
        amenity_id = data.get('amenity_id', '').strip()
        
        if not all([description, complaint_type, amenity_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get student's warden
            cursor.execute(
                "SELECT w.WardenID FROM Warden w WHERE w.HId = %s LIMIT 1",
                (hostel_id,)
            )
            warden_result = cursor.fetchone()
            
            if not warden_result:
                conn.close()
                return jsonify({'error': 'No warden assigned to hostel'}), 400
            
            warden_id = warden_result['WardenID']
            
            # Generate complaint ID
            cursor.execute("SELECT COUNT(*) as cnt FROM Complaint")
            count = cursor.fetchone()['cnt']
            complaint_id = f"C{hostel_id}{count + 1}"
            
            # Prepare complaint data
            room_id = None
            washroom_id = None
            filter_id = None
            
            if complaint_type == 'Room':
                room_id = amenity_id
            elif complaint_type == 'Washroom':
                washroom_id = amenity_id
            elif complaint_type == 'Filter':
                filter_id = amenity_id
            else:
                return jsonify({'error': 'Invalid complaint type'}), 400
            
            # Insert complaint
            insert_query = """
            INSERT INTO Complaint 
            (CId, description, Status, date_time, SId, WardenID, HId, RNo, WashroomID, FId)
            VALUES (%s, %s, 'Pending', %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                complaint_id,
                description,
                datetime.now(),
                student_id,
                warden_id,
                hostel_id,
                room_id,
                washroom_id,
                filter_id
            ))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'complaint_id': complaint_id,
                'message': 'Complaint filed successfully'
            }), 201
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error filing complaint: {str(e)}")
        return jsonify({'error': 'Failed to file complaint'}), 500

@app.route('/api/student/complaints', methods=['GET'])
def get_student_complaints():
    """
    Retrieve all complaints filed by the logged-in student.
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        student_id = session['user']['id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
            SELECT 
                CId, description, Status, date_time,
                RNo, WashroomID, FId
            FROM Complaint
            WHERE SId = %s
            ORDER BY date_time DESC
            """
            
            cursor.execute(query, (student_id,))
            complaints = cursor.fetchall()
            
            # Convert datetime objects to strings
            for complaint in complaints:
                complaint['date_time'] = complaint['date_time'].isoformat()
                complaint['complaint_type'] = (
                    'Room' if complaint['RNo'] else
                    'Washroom' if complaint['WashroomID'] else
                    'Filter'
                )
                complaint['amenity_id'] = (
                    complaint['RNo'] or complaint['WashroomID'] or complaint['FId']
                )
            
            return jsonify({
                'success': True,
                'complaints': complaints
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error retrieving complaints: {str(e)}")
        return jsonify({'error': 'Failed to retrieve complaints'}), 500

@app.route('/api/student/confirm-resolution/<complaint_id>', methods=['POST'])
def confirm_resolution(complaint_id):
    """
    Student confirms the resolution of a complaint marked as 'Resolved' by warden.
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        student_id = session['user']['id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Verify complaint belongs to student and is in Resolved status
            cursor.execute(
                "SELECT * FROM Complaint WHERE CId = %s AND SId = %s AND Status = 'Resolved'",
                (complaint_id, student_id)
            )
            complaint = cursor.fetchone()
            
            if not complaint:
                conn.close()
                return jsonify({'error': 'Complaint not found or not in Resolved status'}), 404
            
            # Update status to Confirmed
            cursor.execute(
                "UPDATE Complaint SET Status = 'Confirmed' WHERE CId = %s",
                (complaint_id,)
            )
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Resolution confirmed successfully'
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error confirming resolution: {str(e)}")
        return jsonify({'error': 'Failed to confirm resolution'}), 500

# ==================== WARDEN API ENDPOINTS ====================

@app.route('/api/warden/complaints', methods=['GET'])
def get_warden_complaints():
    """
    Retrieve all complaints assigned to the logged-in warden.
    Filtered by Hostel ID and Warden ID.
    """
    if 'user' not in session or session['user']['role'] != 'warden':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        warden_id = session['user']['id']
        hostel_id = session['user']['hostel_id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
            SELECT 
                c.CId, c.description, c.Status, c.date_time,
                c.SId, s.SName, s.Smail,
                c.RNo, c.WashroomID, c.FId,
                c.HId
            FROM Complaint c
            JOIN Student s ON c.SId = s.SId
            WHERE c.WardenID = %s AND c.HId = %s
            ORDER BY c.date_time DESC
            """
            
            cursor.execute(query, (warden_id, hostel_id))
            complaints = cursor.fetchall()
            
            # Convert datetime objects to strings
            for complaint in complaints:
                complaint['date_time'] = complaint['date_time'].isoformat()
                complaint['complaint_type'] = (
                    'Room' if complaint['RNo'] else
                    'Washroom' if complaint['WashroomID'] else
                    'Filter'
                )
                complaint['amenity_id'] = (
                    complaint['RNo'] or complaint['WashroomID'] or complaint['FId']
                )
            
            return jsonify({
                'success': True,
                'complaints': complaints
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error retrieving warden complaints: {str(e)}")
        return jsonify({'error': 'Failed to retrieve complaints'}), 500

@app.route('/api/warden/complaint/<complaint_id>/resolve', methods=['PUT'])
def resolve_complaint(complaint_id):
    """
    Warden marks a complaint as 'Resolved'.
    """
    if 'user' not in session or session['user']['role'] != 'warden':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        warden_id = session['user']['id']
        hostel_id = session['user']['hostel_id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Verify complaint exists and belongs to warden
            cursor.execute(
                "SELECT * FROM Complaint WHERE CId = %s AND WardenID = %s AND HId = %s",
                (complaint_id, warden_id, hostel_id)
            )
            complaint = cursor.fetchone()
            
            if not complaint:
                conn.close()
                return jsonify({'error': 'Complaint not found'}), 404
            
            # Update status to Resolved
            cursor.execute(
                "UPDATE Complaint SET Status = 'Resolved' WHERE CId = %s",
                (complaint_id,)
            )
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Complaint marked as resolved'
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error resolving complaint: {str(e)}")
        return jsonify({'error': 'Failed to resolve complaint'}), 500

@app.route('/api/warden/stats', methods=['GET'])
def get_warden_stats():
    """
    Retrieve statistics for warden dashboard.
    """
    if 'user' not in session or session['user']['role'] != 'warden':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        warden_id = session['user']['id']
        hostel_id = session['user']['hostel_id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Total complaints
            cursor.execute(
                "SELECT COUNT(*) as count FROM Complaint WHERE WardenID = %s AND HId = %s",
                (warden_id, hostel_id)
            )
            total = cursor.fetchone()['count']
            
            # Pending complaints
            cursor.execute(
                "SELECT COUNT(*) as count FROM Complaint WHERE WardenID = %s AND HId = %s AND Status = 'Pending'",
                (warden_id, hostel_id)
            )
            pending = cursor.fetchone()['count']
            
            # Resolved complaints
            cursor.execute(
                "SELECT COUNT(*) as count FROM Complaint WHERE WardenID = %s AND HId = %s AND Status = 'Resolved'",
                (warden_id, hostel_id)
            )
            resolved = cursor.fetchone()['count']
            
            # Confirmed complaints
            cursor.execute(
                "SELECT COUNT(*) as count FROM Complaint WHERE WardenID = %s AND HId = %s AND Status = 'Confirmed'",
                (warden_id, hostel_id)
            )
            confirmed = cursor.fetchone()['count']
            
            return jsonify({
                'success': True,
                'stats': {
                    'total': total,
                    'pending': pending,
                    'resolved': resolved,
                    'confirmed': confirmed
                }
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error retrieving stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
