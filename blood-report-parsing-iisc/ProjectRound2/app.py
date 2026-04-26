from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import helper
import os
import json
import pandas as pd
import atexit
import sqlite3
import hashlib
from functools import wraps
import random
import string
from datetime import datetime, timedelta
import pytz
import pymupdf 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")

class ParseError(Exception):
    pass

class BloodReportError(Exception):
    pass

class PlotGenerationError(Exception):
    pass

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY", os.urandom(24))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PLOTS_FOLDER'] = 'static/plots'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.secret_key = app.config['SECRET_KEY']  
app.config['PERMANENT_SESSION_LIFETIME'] = 1800 


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

def get_db():
    db = sqlite3.connect('blood_reports.db')
    db.row_factory = sqlite3.Row
    return db


def is_multiple_blood_reports(file_path):
    doc = pymupdf.open(file_path)
    if len(doc) > 1:
        return True  
    return False

def init_db():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK( role IN ('patient', 'doctor', 'admin')) NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            parsed_report TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ResetTokens (
            token_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        )""")
        db.commit()

init_db()

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        if not '.' in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Allowed types: PDF, JPG, JPEG, PNG'}), 400
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        case = 0
        try:
            file.save(file_path)
            if(is_multiple_blood_reports(file_path)):
                case  = 1
                print(f"{file_path} a multi test blood report")
            print(f"File saved successfully: {file_path}")
        except Exception as e:
            print(f"File save error: {str(e)}")
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        try:
            print(f"Processing file: {file_path}")
            if(not case):
                parsed_report = helper.get_parsed_report(file_path)
            else: 
                parsed_report = helper.get_parsed_multi_report(file_path)    
            print("Report parsed successfully")

            report_dict = parsed_report.dict() if hasattr(parsed_report, 'dict') else parsed_report
            try:
                print("Generating plots...")
                helper.create_blood_test_plots(parsed_report, "static/plots")
                print("Plots generated successfully")
            except Exception as e:
                print(f"Warning: Plot generation failed: {str(e)}")
            try: 
                print("Getting medical insights...")
                insights = helper.get_medical_insights_n_recommendataions(parsed_report)
                print("Medical insights generated successfully")
            except Exception as e:
                print(e)
                print("Insight Generation went unsuccessful.")
            if not case:
                with get_db() as db:
                    cursor = db.cursor() 
                    parsed_report_dict = parsed_report.dict() if hasattr(parsed_report, 'dict') else parsed_report
                    patient_info = parsed_report_dict.get('patient_info', {})
                    cursor.execute("""
                        INSERT OR IGNORE INTO Patients (user_id, name, age, gender)
                        VALUES (?, ?, ?, ?)
                    """, (
                        session['user_id'],
                        patient_info.get('name'),
                        patient_info.get('age').split()[0],
                        patient_info.get('gender')
                    ))
                    cursor.execute("SELECT COUNT(*) FROM Patients")
                    try:
                        patient_id = cursor.fetchone()[0]  
                    except Exception as e:
                        print(e)
                    ist = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %z')
                    cursor.execute("""
                        INSERT INTO Reports (patient_id, parsed_report, uploaded_at)
                        VALUES (?, ?, ?)
                    """, (patient_id, json.dumps(parsed_report_dict), current_time))
                    db.commit()
                    print("Patient and Report have been successfully stored into database.")
            response_data = {
                'success': True,
                'report': report_dict,
                'insights': insights,
            }
            return jsonify(response_data)
        except Exception as e:
            print(f"Error in upload endpoint: {str(e)}")
            return jsonify({'error': f'Failed to process report: {str(e)}'}), 422
        finally:
            try:
                os.remove(file_path)
                print(f"Cleaned up file: {file_path}")
            except Exception as e:
                print(f"Cleanup error: {str(e)}")
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try: 
        print("Chat has been initiated.")
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 40
        message = data.get('message')
        current_report = data.get('report')
        session_id = data.get('session_id', f"chat_{session['user_id']}")  
        if not message or not current_report:
            return jsonify({'error': 'Missing message or report data'}), 400
        role = session.get('role', 'patient') 
        previous_reports = "No Previous Reports Available"
        if(len(current_report)>2):
            patient_name = current_report.get('patient_info', {}).get('name')
            if not patient_name:
                return jsonify({'error': 'Patient name not found in report'}), 400
            previous_reports = helper.get_patient_report_history(patient_name, session['user_id'])
        try:
            response = helper.get_chat_response(
                message=message,
                role=role,
                current_report=current_report,
                previous_reports=previous_reports,
                session_id=session_id
            )
            if not response:
                return jsonify({'error': 'No response generated'}), 500
            return jsonify({'response': response})
        except Exception as e:
            print(f"Error generating chat response: {str(e)}")
            return jsonify({'error': f'Failed to generate response: {str(e)}'}), 500
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400
        hashed_password = hash_password(password)
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM Users WHERE email = ? AND password = ?",
                (email, hashed_password)
            )
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['user_id']
                session['role'] = user['role']  
                session['name'] = user['name']
                return jsonify({
                    'success': True,
                    'user': {
                        'name': user['name'],
                        'role': user['role']
                    }
                })
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = hash_password(data['password'])
        role = data['role']
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role)
            )
            db.commit()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True})

def cleanup_plots():
    upload_dir = app.config['PLOTS_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            try:
                file_path = os.path.join(upload_dir, filename)
                os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up {filename}: {e}")

def cleanup_uploads():
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            try:
                file_path = os.path.join(upload_dir, filename)
                os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up {filename}: {e}")

def cleanup_trend_analysis():
    trend_analysis_path = os.path.join('static', 'trend_analysis.html')
    if os.path.exists(trend_analysis_path):
        try:
            os.remove(trend_analysis_path)
        except Exception as e:
            print(f"Error removing {trend_analysis_path}: {e}")

atexit.register(cleanup_uploads)
atexit.register(cleanup_plots)
atexit.register(cleanup_trend_analysis)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/get_patients', methods=['GET'])
@login_required
def get_patients():
    try:
        user_id = session.get('user_id')
        patients = helper.get_patient_names_from_db_wrt_user(user_id)
        return jsonify({'patients': patients})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_test_names', methods=['POST'])
@login_required
def get_test_names():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        patient_name = data.get('patient_name')
        if not patient_name:
            return jsonify({'error': 'Patient name is required'}), 400
        test_names = helper.get_report_ids_n_test_names(patient_name, user_id)
        print("--------------------------------")
        print("------Test Names------------")
        print(test_names)
        print("--------------------------------")
        grouped_tests = helper.grouping_test_names(test_names)
        print("--------------------------------")
        print("------Grouping tests------------")
        print(grouped_tests)
        print("--------------------------------")
        return jsonify(grouped_tests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_lab_results', methods=['POST'])
@login_required
def get_lab_results():
    try:
        data = request.get_json()
        report_ids = data.get('report_ids')
        if not report_ids:
            return jsonify({'error': 'Report IDs are required'}), 400
        lab_results = helper.get_lab_results_for_test(report_ids)
        print("-----------Lab Results-------------")
        print(lab_results)
        print("-----------------------------------")
        mapping = helper.standardizing_param_names_with_llm(lab_results)
        print("-----------Mapping-------------")
        print(mapping)
        print("-----------------------------------")
        df = helper.apply_standardized_names(lab_results, mapping)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df_numeric = df.select_dtypes(include=["float64", "int64"])
        df[df_numeric.columns] = df_numeric.interpolate(method="linear")
        df = df.fillna("Not Available")
        print("---------STD AND PROCESSED DF------------")
        session['trend_df'] = df.to_json()
        print(df)
        print("-----------------------------------------")
        report_path = os.path.join(app.static_folder, 'trend_analysis.html')
        helper.generate_pandas_profiling_report(df, report_path)
        print("-----------------------------------------------")
        print('------------DataFrame------------------------')
        print(df)
        print("-----------------------------------------------")
        parameters = sorted(df.drop('report_id',axis=1).columns.tolist())
        print("-----------------------------------------------")
        print('------------Parameters------------------------')
        print(parameters)
        print("-----------------------------------------------")
        return jsonify({
            'lab_results': lab_results,
            'parameters': parameters,
            'report_url': url_for('static', filename='trend_analysis.html')
        })
    except Exception as e:
        print(f"Error in get_lab_results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_parameter_trend', methods=['POST'])
@login_required
def get_parameter_trend():
    try:
        data = request.get_json()
        selected_param = data.get('parameter')
        if not selected_param:
            return jsonify({'error': 'Parameter is required'}), 400
        if 'trend_df' not in session:
            return jsonify({'error': 'Please select a test first'}), 400
        df = pd.read_json(session['trend_df'])
        print('------------DataFrame------------------------')
        print(df)
        print("-----------------------------------------------")
        df_updated = helper.merge_uploaded_timestamps(df)
        print('------------Updated DataFrame------------------------')
        print(df)
        print("-----------------------------------------------")
        plot_path = helper.plot_scatter(df_updated, selected_param)
        return jsonify({
            'plot_url': url_for('static', filename=plot_path)
        }) if plot_path else jsonify({'error': 'Failed to generate plot'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_email(to_email, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASSWORD')
    if not sender_email or not sender_password:
        raise RuntimeError('SMTP_EMAIL and SMTP_PASSWORD must be set')
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT user_id FROM Users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        otp = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)
        cursor.execute("""
            INSERT INTO ResetTokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        """, (user['user_id'], otp, expires_at))
        db.commit()
        email_body = f"Your OTP for password reset is: {otp}\nThis OTP will expire in 10 minutes."
        if send_email(email, 'Password Reset OTP', email_body):
            return jsonify({'message': 'OTP sent successfully'})
        return jsonify({'error': 'Failed to send OTP'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.json.get('email')
    otp = request.json.get('otp')
    new_password = request.json.get('new_password')
    if not all([email, otp, new_password]):
        return jsonify({'error': 'Email, OTP and new password are required'}), 400
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT user_id FROM Users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        cursor.execute("""
            SELECT * FROM ResetTokens
            WHERE user_id = ? AND token = ? AND used = 0 AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC LIMIT 1
        """, (user['user_id'], otp))
        token = cursor.fetchone()
        if not token:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        cursor.execute('UPDATE ResetTokens SET used = 1 WHERE token_id = ?', (token['token_id'],))
        hashed_password = hash_password(new_password)
        cursor.execute('UPDATE Users SET password = ? WHERE user_id = ?', 
                      (hashed_password, user['user_id']))
        db.commit()
        return jsonify({'message': 'Password reset successful'})

@app.route('/api/user_patients_with_reports', methods=['GET'])
@login_required
def get_user_patients_with_reports():
    try:
        user_id = session.get('user_id')
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT DISTINCT p.name, p.patient_id
                FROM Patients p
                JOIN Reports r ON p.patient_id = r.patient_id
                WHERE p.user_id = ?
                ORDER BY p.name
            """, (user_id,))
            patients = cursor.fetchall()
            result = []
            for patient in patients:
                patient_name, patient_id = patient
                cursor.execute("""
                    SELECT r.uploaded_at, r.report_id, r.parsed_report
                    FROM Reports r
                    WHERE r.patient_id = ?
                    ORDER BY r.uploaded_at DESC
                """, (patient_id,))
                reports = [{
                    'timestamp': row[0],
                    'report_id': row[1],
                    'parsed_report': json.loads(row[2])
                } for row in cursor.fetchall()]
                result.append({
                    'name': patient_name,
                    'patient_id': patient_id,
                    'reports': reports
                })
            
            return jsonify({'patients': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patient_reports/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_reports(patient_id):
    try:
        user_id = session.get('user_id')
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM Patients WHERE patient_id = ? AND user_id = ?", (patient_id, user_id))
            if not cursor.fetchone():
                return jsonify({'error': 'Unauthorized access'}), 403
            cursor.execute("""
                SELECT report_id, uploaded_at, parsed_report
                FROM Reports
                WHERE patient_id = ?
                ORDER BY uploaded_at DESC
            """, (patient_id,))
            reports = [{
                'report_id': row[0],
                'uploaded_at': row[1],
                'parsed_report': json.loads(row[2])
            } for row in cursor.fetchall()]
            return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
