from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from agents import receive_symptom_message, SYMPTOM_CONVERSATION
from langchain_core.messages import HumanMessage, AIMessage
import os
import datetime
import pickle
import json
from werkzeug.utils import secure_filename
from typing import List
import traceback
# Add these imports at the top of the file
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import mimetypes


# Try importing Google API client
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Google API client not available. Calendar integration will be simulated.")

# Add after importing os
# Email configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "saikiranpatnana5143@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "ohzc idub grps czwb") 
# Load environment variables
app = Flask(__name__, static_folder="static")
app.secret_key = "hackwave2025"  # Add a secret key for session management

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Sample doctors data
DOCTORS = [
    {
        "id": "1",
        "name": "Sarah Johnson",
        "specialization": "Gastroenterologist",
        "experience": 12,
        "languages": "English, Spanish",
        "consultation_fee": 1500,
        "rating": 4.9,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"]
    },
    {
        "id": "2",
        "name": "Robert Chen",
        "specialization": "Cardiologist",
        "experience": 15,
        "languages": "English, Mandarin",
        "consultation_fee": 1800,
        "rating": 4.8,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["10:00 AM", "01:00 PM", "03:30 PM", "05:00 PM"]
    },
    {
        "id": "3",
        "name": "Priya Sharma",
        "specialization": "Dermatologist",
        "experience": 10,
        "languages": "English, Hindi",
        "consultation_fee": 1200,
        "rating": 4.7,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["09:30 AM", "12:00 PM", "02:30 PM", "04:00 PM"]
    },
    {
        "id": "4",
        "name": "Michael Wilson",
        "specialization": "Neurologist",
        "experience": 14,
        "languages": "English",
        "consultation_fee": 2000,
        "rating": 4.9,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["08:30 AM", "11:00 AM", "01:30 PM", "05:30 PM"]
    },
    {
        "id": "5",
        "name": "Lisa Thompson",
        "specialization": "Psychiatrist",
        "experience": 11,
        "languages": "English, French",
        "consultation_fee": 1600,
        "rating": 4.6,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["10:30 AM", "12:30 PM", "03:00 PM", "05:30 PM"]
    },
    {
        "id": "6",
        "name": "Alex Patel",
        "specialization": "Orthopedic Surgeon",
        "experience": 16,
        "languages": "English, Gujarati",
        "consultation_fee": 2200,
        "rating": 4.8,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["08:00 AM", "10:30 AM", "02:00 PM", "04:30 PM"]
    },
    {
        "id": "7",
        "name": "David Kim",
        "specialization": "Pulmonologist",
        "experience": 13,
        "languages": "English, Korean",
        "consultation_fee": 1700,
        "rating": 4.7,
        "email": "saikiranpatnana3143@gmail.com",
        "available_slots": ["09:00 AM", "11:30 AM", "03:30 PM", "05:00 PM"]
    }
]

# Add this function for sending emails with attachments
def send_email_with_attachments(sender_email, sender_password, recipient_email, 
                               subject, body, attachment_list=None):
    """
    Send an email with attachments to the recipient
    
    Parameters:
    - sender_email: Email address used to send the message
    - sender_password: Password for the sender email (use app password for Gmail)
    - recipient_email: Email address of the recipient
    - subject: Email subject line
    - body: Email body text (can be HTML)
    - attachment_list: List of dictionaries containing file info (path, filename, type)
    
    Returns:
    - dict: Success status and message
    """
    try:
        print(f"Sending email to {recipient_email}...")
        
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        
        # Add body to email
        message.attach(MIMEText(body, 'html'))
        
        # Add attachments if provided
        if attachment_list:
            for attachment in attachment_list:
                file_path = attachment.get('path')
                
                if not file_path or not os.path.exists(file_path):
                    print(f"Skipping attachment - file not found: {file_path}")
                    continue
                
                filename = attachment.get('filename') or os.path.basename(file_path)
                content_type = attachment.get('type')
                
                # Determine content type if not provided
                if not content_type:
                    content_type, encoding = mimetypes.guess_type(file_path)
                    if content_type is None:
                        content_type = "application/octet-stream"
                
                main_type, sub_type = content_type.split('/', 1)
                
                try:
                    with open(file_path, 'rb') as file:
                        if main_type == 'application' or main_type == 'image':
                            attachment_part = MIMEApplication(file.read(), _subtype=sub_type)
                            attachment_part.add_header('Content-Disposition', 'attachment', filename=filename)
                        else:
                            attachment_part = MIMEBase(main_type, sub_type)
                            attachment_part.set_payload(file.read())
                            encoders.encode_base64(attachment_part)
                            attachment_part.add_header('Content-Disposition', 'attachment', filename=filename)
                        
                        message.attach(attachment_part)
                    print(f"Attached file: {filename}")
                except Exception as e:
                    print(f"Error attaching file {filename}: {str(e)}")
        
        # Connect to mail server
        # For Gmail, use:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        
        print(f"Logging in as {sender_email}...")
        
        # Login to sender email (using app password for Gmail)
        server.login(sender_email, sender_password)
        
        # Send email
        print("Sending email...")
        server.send_message(message)
        print("Email sent successfully!")
        server.quit()
        
        return {
            "success": True,
            "message": f"Email sent successfully to {recipient_email}"
        }
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def authenticate_google_calendar():
    """Authenticate and return Google Calendar API service instance."""
    if not GOOGLE_API_AVAILABLE:
        return None
        
    try:
        creds = None
        token_path = "token.pickle"
        
        # Check if token file exists
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        print(creds.valid)     
        if not creds or not creds.valid:
            print("Google Calendar credentials not valid or missing.")
            return None
            
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        print(f"Error authenticating with Google Calendar: {str(e)}")
        return None

def schedule_meet_with_notification(scheduled_time, doctor_email, patient_email, description=None, attachments=None):
    """Schedule a Google Meet and notify both doctor & patient via email."""
    service = authenticate_google_calendar()
    
    # Default to succeed for mock mode
    calendar_success = True
    meet_link = "https://meet.google.com/abc-defg-hij"  # Default mock link
    
    # Try to create actual Google Calendar event if API is available
    if service:
        try:
            print(f"Scheduling meeting with datetime: '{scheduled_time}'")
            
            # Parse the datetime string
            try:
                start_time = datetime.datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            except ValueError as e:
                print(f"Error parsing datetime: {e}")
                # Try alternative format
                start_time = datetime.datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
            
            end_time = start_time + datetime.timedelta(minutes=30)  # 30-minute meeting
            
            # Convert to ISO format
            start_time_iso = start_time.isoformat()
            end_time_iso = end_time.isoformat()
            
            # Use provided description or fallback to default
            event_description = description if description else "Your online consultation is scheduled."
            
            # Event details
            event = {
                "summary": "Doctor Appointment",
                "description": event_description,
                "start": {
                    "dateTime": start_time_iso,
                    "timeZone": "Asia/Kolkata",  # Ensure correct timezone
                },
                "end": {
                    "dateTime": end_time_iso,
                    "timeZone": "Asia/Kolkata",
                },
                "attendees": [
                    {"email": doctor_email},
                    {"email": patient_email},
                ],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"meet-{start_time.strftime('%Y%m%d%H%M')}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                }
            }
            
            # Create event
            event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all"  # This sends basic email notifications
            ).execute()
            
            meet_link = event.get("hangoutLink", "")
            calendar_success = True
            
        except Exception as e:
            print(f"Error creating Google Meet: {str(e)}")
            traceback.print_exc()
            calendar_success = False
    else:
        print("Using mock Google Meet integration because credentials aren't available")
    
    # Now send a detailed email with attachments to the doctor
    # (whether or not Calendar API worked)
    if doctor_email:  # Only proceed if we have a doctor email
        try:
            # CHANGE THIS SECTION - Use your global variables defined at the top of the file
            sender_email = EMAIL_SENDER
            sender_password = EMAIL_PASSWORD
            
            # Create a nice HTML email body
            email_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .header {{ background-color: #3367d6; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .section {{ margin-bottom: 20px; }}
                        .section-title {{ color: #3367d6; font-size: 18px; font-weight: bold; }}
                        .appointment-info {{ background-color: #f5f7fa; border-left: 4px solid #3367d6; padding: 15px; }}
                        .meet-link {{ padding: 15px; background-color: #ebf3fe; border-radius: 5px; }}
                        .meet-link a {{ color: #3367d6; text-decoration: none; font-weight: bold; }}
                        pre {{ white-space: pre-wrap; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>MediAssist: New Patient Appointment</h2>
                    </div>
                    <div class="content">
                        <div class="section">
                            <p>Dear Doctor,</p>
                            <p>A new patient appointment has been scheduled for you.</p>
                        </div>
                        
                        <div class="section appointment-info">
                            <p><strong>Patient Email:</strong> {patient_email}</p>
                            <p><strong>Date & Time:</strong> {scheduled_time}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Symptom Analysis</div>
                            <pre>{description}</pre>
                        </div>
                        
                        <div class="section">
                            <div class="meet-link">
                                <p><strong>Google Meet Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
                                <p>Click the link above at the scheduled time to join the consultation.</p>
                            </div>
                        </div>
                        
                        <div class="section">
                            <p>Patient medical records are attached to this email for your review.</p>
                            <p>Thank you for using MediAssist.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Send email with attachments - CHANGE THIS CONDITION
            if sender_email == "saikiranpatnana5143@gmail.com" and sender_password == "ohzc idub grps czwb":
                # Only attempt to send if credentials are provided
                email_result = send_email_with_attachments(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=doctor_email,
                    subject="New Patient Appointment with Medical Records",
                    body=email_body,
                    attachment_list=attachments
                )
                
                if email_result["success"]:
                    print(f"Email with attachments sent to {doctor_email}")
                else:
                    print(f"Failed to send email: {email_result['message']}")
            else:
                print("Email credentials not configured. Skipping email with attachments.")
                print(f"Would send email to {doctor_email} with {len(attachments) if attachments else 0} attachments")
        
        except Exception as e:
            print(f"Error sending email with attachments: {str(e)}")
            traceback.print_exc()
    
    # Return the overall result
    return {
        "success": calendar_success,
        "meet_link": meet_link,
        "message": "Google Meet created successfully" if calendar_success else "Failed to create Google Meet but email was sent"
    }
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def home_page():
    return render_template('index.html')

@app.route('/sel_sym')
def sym_page():
    return render_template('symptoms.html')

@app.route('/sel_sym1')
def sym_page1():
    return render_template('sex.html')

@app.route('/sel_sym2')
def sym_page2():
    return render_template('add_sym.html')

@app.route('/symptom_analysis')
def symptom_analysis():
    # Clear the conversation for a fresh start
    global SYMPTOM_CONVERSATION
    SYMPTOM_CONVERSATION.clear()
    
    # Get symptoms from session if available
    initial_symptoms = session.get('initial_symptoms', '')
    
    # Add welcome message
    welcome_message = AIMessage(content="""
👋 Hello!

I'm your AI Medical Assistant. I'm here to help analyze your symptoms and connect you with the right healthcare professionals.
""")
    SYMPTOM_CONVERSATION.append(welcome_message)
    
    if initial_symptoms:
        # Parse symptoms into a list
        symptoms_list = [s.strip() for s in initial_symptoms.split(',') if s.strip()]
        
        if symptoms_list:
            # Initialize conversation with symptoms
            initial_message = f"I have the following symptoms: {', '.join(symptoms_list)}"
            # Process this initial message
            receive_symptom_message(initial_message)
    
    # Render the symptom analysis template with the conversation
    return render_template('symptom_analysis.html', conversation=SYMPTOM_CONVERSATION)

@app.route('/predict_1', methods=['POST'])
def predict_1():
    # Get the symptoms from the form
    selected_symptoms = request.form.get('selected_symptoms', '')
    selected_symptoms_frommodel = request.form.get('selected_symptoms_frommodel', '')
    
    # Combine the symptoms
    all_symptoms = selected_symptoms
    if selected_symptoms_frommodel:
        all_symptoms += ", " + selected_symptoms_frommodel if selected_symptoms else selected_symptoms_frommodel
    
    # Store symptoms in session
    session['initial_symptoms'] = all_symptoms
    
    # Redirect to the symptom analysis page
    return redirect(url_for('symptom_analysis'))

@app.route('/api/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        message = data.get('message')
        print(f"Received message API call: {message}")
        
        # Get the current conversation length
        current_length = len(SYMPTOM_CONVERSATION)
        
        # Process the message with our simplified chatbot
        result = receive_symptom_message(message)
        
        # Find only the new AI message that was added during processing
        if len(SYMPTOM_CONVERSATION) > current_length:
            response = SYMPTOM_CONVERSATION[-1].content
        else:
            response = "I'm processing your message..."
        
        return jsonify({
            'message': response,
            'show_booking': result.get('show_booking', False),
            'symptom_details': result.get('symptom_details', {})
        })
    except Exception as e:
        print(f"API ERROR: {str(e)}")
        return jsonify({
            'message': "I apologize for the technical difficulties. Please try again.",
            'show_booking': False
        })

@app.route('/book_appointment')
def book_appointment():
    """Route for booking appointments with specialists"""
    
    # Get the last AI message from conversation as summary
    summary = ""
    
    if SYMPTOM_CONVERSATION:
        # First, look for the final AI message that contains a recommendation
        for msg in reversed(SYMPTOM_CONVERSATION):
            if isinstance(msg, AIMessage) and any(word in msg.content.lower() for word in 
                                                ["recommend", "specialist", "doctor", "appointment"]):
                summary = msg.content
                break
        
        # If no recommendation found, use the last AI message
        if not summary:
            for msg in reversed(SYMPTOM_CONVERSATION):
                if isinstance(msg, AIMessage):
                    summary = msg.content
                    break
        
        # Store the summary in session for future use
        session['symptom_summary'] = summary
    
    # Get recommended specialist type from summary (if available)
    recommended_specialist = "General Practitioner"  # default
    specialist_types = ["Gastroenterologist", "Cardiologist", "Dermatologist", 
                       "Neurologist", "Psychiatrist", "Orthopedic", "Pulmonologist"]
    
    if summary:
        for specialist in specialist_types:
            if specialist.lower() in summary.lower():
                recommended_specialist = specialist
                break
    
    # Filter doctors by recommended specialization
    filtered_doctors = [d for d in DOCTORS if recommended_specialist.lower() in d["specialization"].lower()]
    
    # If no matching doctors, show all doctors
    if not filtered_doctors:
        filtered_doctors = DOCTORS
    
    # Process the summary with markdown
    try:
        from markdown import markdown
        # Convert markdown to HTML for the template
        summary_html = markdown(summary) if summary else ""
    except ImportError:
        # Fallback if markdown package not available
        summary_html = summary.replace('\n', '<br>') if summary else ""
    
    # Render the booking template with doctors and summary
    return render_template('book_appointment.html', 
                          doctors=filtered_doctors, 
                          summary=summary_html,
                          email=session.get('patient_email', ''))
def schedule_meet_with_notification(scheduled_time, doctor_email, patient_email, description=None, attachments=None):
    """Schedule a Google Meet and notify both doctor & patient via email."""
    service = authenticate_google_calendar()
    
    # Default to succeed for mock mode
    calendar_success = True
    meet_link = "https://meet.google.com/abc-defg-hij"  # Default mock link
    
    # Try to create actual Google Calendar event if API is available
    if service:
        try:
            print(f"Scheduling meeting with datetime: '{scheduled_time}'")
            
            # Parse the datetime string
            try:
                start_time = datetime.datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            except ValueError as e:
                print(f"Error parsing datetime: {e}")
                # Try alternative format
                start_time = datetime.datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
            
            end_time = start_time + datetime.timedelta(minutes=30)  # 30-minute meeting
            
            # Convert to ISO format
            start_time_iso = start_time.isoformat()
            end_time_iso = end_time.isoformat()
            
            # Use provided description or fallback to default
            event_description = description if description else "Your online consultation is scheduled."
            
            # Event details
            event = {
                "summary": "Doctor Appointment",
                "description": event_description,
                "start": {
                    "dateTime": start_time_iso,
                    "timeZone": "Asia/Kolkata",  # Ensure correct timezone
                },
                "end": {
                    "dateTime": end_time_iso,
                    "timeZone": "Asia/Kolkata",
                },
                "attendees": [
                    {"email": doctor_email},
                    {"email": patient_email},
                ],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"meet-{start_time.strftime('%Y%m%d%H%M')}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                }
            }
            
            # Create event
            event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all"  # This sends basic email notifications
            ).execute()
            
            meet_link = event.get("hangoutLink", "")
            calendar_success = True
            
        except Exception as e:
            print(f"Error creating Google Meet: {str(e)}")
            traceback.print_exc()
            calendar_success = False
    else:
        print("Using mock Google Meet integration because credentials aren't available")
    
    # Get doctor details for emails
    doctor_info = next((d for d in DOCTORS if d["email"] == doctor_email), {"name": "Your Doctor", "specialization": "Specialist"})
    
    # Get the symptom summary (IMPORTANT: this is the part we're fixing)
    symptom_summary = description.split("----- SPECIALIST RECOMMENDATION -----")[-1].strip() if description else ""
    
    # Email credentials
    sender_email = EMAIL_SENDER
    sender_password = EMAIL_PASSWORD
    
    if doctor_email:  # Only proceed if we have a doctor email
        try:
            # Create a nice HTML email body FOR DOCTOR
            doctor_email_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .header {{ background-color: #3367d6; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .section {{ margin-bottom: 20px; }}
                        .section-title {{ color: #3367d6; font-size: 18px; font-weight: bold; }}
                        .appointment-info {{ background-color: #f5f7fa; border-left: 4px solid #3367d6; padding: 15px; }}
                        .meet-link {{ padding: 15px; background-color: #ebf3fe; border-radius: 5px; }}
                        .meet-link a {{ color: #3367d6; text-decoration: none; font-weight: bold; }}
                        pre {{ white-space: pre-wrap; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>MediAssist: New Patient Appointment</h2>
                    </div>
                    <div class="content">
                        <div class="section">
                            <p>Dear Doctor,</p>
                            <p>A new patient appointment has been scheduled for you.</p>
                        </div>
                        
                        <div class="section appointment-info">
                            <p><strong>Patient Email:</strong> {patient_email}</p>
                            <p><strong>Date & Time:</strong> {scheduled_time}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Symptom Analysis</div>
                            <div>{description}</div>
                        </div>
                        
                        <div class="section">
                            <div class="meet-link">
                                <p><strong>Google Meet Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
                                <p>Click the link above at the scheduled time to join the consultation.</p>
                            </div>
                        </div>
                        
                        <div class="section">
                            <p>Patient medical records are attached to this email for your review.</p>
                            <p>Thank you for using MediAssist.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Try to send email to doctor
            if sender_email and sender_password:
                email_result = send_email_with_attachments(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=doctor_email,
                    subject="New Patient Appointment with Medical Records",
                    body=doctor_email_body,
                    attachment_list=attachments
                )
                
                if email_result["success"]:
                    print(f"Email with attachments sent to doctor: {doctor_email}")
                else:
                    print(f"Failed to send email to doctor: {email_result['message']}")
            else:
                print("Email credentials not configured. Skipping email with attachments.")
        
        except Exception as e:
            print(f"Error sending email to doctor: {str(e)}")
            traceback.print_exc()
    
    # Also send email to patient without attachments
    if patient_email:
        try:
            # Create a nice HTML email body FOR PATIENT
            patient_email_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .header {{ background-color: #3367d6; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .section {{ margin-bottom: 20px; }}
                        .section-title {{ color: #3367d6; font-size: 18px; font-weight: bold; }}
                        .appointment-info {{ background-color: #f5f7fa; border-left: 4px solid #3367d6; padding: 15px; }}
                        .meet-link {{ padding: 15px; background-color: #ebf3fe; border-radius: 5px; }}
                        .meet-link a {{ color: #3367d6; text-decoration: none; font-weight: bold; }}
                        .doctor-info {{ display: flex; align-items: center; }}
                        .doctor-avatar {{ width: 60px; height: 60px; background: #3367d6; color: white; border-radius: 50%; 
                                          display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 24px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Your Appointment is Confirmed!</h2>
                    </div>
                    <div class="content">
                        <div class="section">
                            <p>Dear Patient,</p>
                            <p>Your appointment with Dr. {doctor_info["name"]} has been scheduled successfully.</p>
                        </div>
                        
                        <div class="section doctor-info">
                            <div class="doctor-avatar">{doctor_info["name"][0]}</div>
                            <div>
                                <h3>Dr. {doctor_info["name"]}</h3>
                                <p>{doctor_info["specialization"]}</p>
                            </div>
                        </div>
                        
                        <div class="section appointment-info">
                            <p><strong>Date & Time:</strong> {scheduled_time}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Your Symptom Analysis</div>
                            <div>{symptom_summary}</div>
                        </div>
                        
                        <div class="section">
                            <div class="meet-link">
                                <p><strong>Google Meet Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
                                <p>Click the link above at the scheduled time to join your consultation.</p>
                            </div>
                        </div>
                        
                        <div class="section">
                            <p>Thank you for using MediAssist.</p>
                            <p>Please be prepared 5 minutes before your appointment time.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Try to send email to patient
            if sender_email and sender_password:
                email_result = send_email_with_attachments(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=patient_email,
                    subject=f"Your Appointment with Dr. {doctor_info['name']} is Confirmed",
                    body=patient_email_body,
                    attachment_list=None  # No attachments for patient
                )
                
                if email_result["success"]:
                    print(f"Confirmation email sent to patient: {patient_email}")
                else:
                    print(f"Failed to send email to patient: {email_result['message']}")
            else:
                print("Email credentials not configured. Skipping patient email.")
                
        except Exception as e:
            print(f"Error sending email to patient: {str(e)}")
            traceback.print_exc()
    
    # Return the overall result
    return {
        "success": calendar_success,
        "meet_link": meet_link,
        "message": "Google Meet created successfully" if calendar_success else "Failed to create Google Meet but email was sent"
    }
@app.route('/appointment_confirmation')
def appointment_confirmation():
    """Show appointment confirmation page"""
    appointment = session.get('last_appointment', {})
    if not appointment:
        flash('No appointment found. Please book an appointment first.')
        return redirect(url_for('book_appointment'))
    
    return render_template('appointment_confirmation.html', appointment=appointment)

@app.route('/api/book_appointment', methods=['POST'])
def api_book_appointment():
    try:
        # Get form data
        doctor_id = request.form.get('doctor_id')
        time_slot = request.form.get('time_slot')
        doctor_email = request.form.get('doctor_email')
        patient_email = request.form.get('patient_email')
        
        print(f"Processing appointment: Doctor ID={doctor_id}, Slot={time_slot}")
        print(f"Doctor Email: {doctor_email}, Patient Email: {patient_email}")
        
        if not all([doctor_id, time_slot, doctor_email, patient_email]):
            return jsonify({
                'success': False,
                'message': 'Missing required information'
            })
        
        # Store patient email for future use
        session['patient_email'] = patient_email
        
        # Find doctor by ID
        doctor = next((d for d in DOCTORS if d['id'] == doctor_id), None)
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor not found'
            })
        
        # Handle file uploads
        uploaded_files = []
        file_paths = []
        
        for key in request.files:
            file = request.files[key]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
                uploaded_files.append({
                    'filename': filename,
                    'path': file_path,
                    'type': file.content_type
                })
                print(f"Uploaded file: {filename}")
        
        # Format the appointment date (today) with the selected time slot
        today = datetime.date.today().strftime("%Y-%m-%d")
        appointment_time = f"{today} {time_slot}"
        
        # Properly format the time for datetime parsing
        formatted_time = time_slot.strip()
        
        # Check if it's AM or PM and convert to 24-hour format
        if "AM" in formatted_time or "PM" in formatted_time:
            try:
                # Parse the time using datetime
                time_obj = datetime.datetime.strptime(formatted_time, "%I:%M %p")
                # Convert to 24-hour format string
                formatted_time = time_obj.strftime("%H:%M")
            except ValueError as e:
                print(f"Error parsing time: {e}")
                formatted_time = "12:00"  # Fallback to noon
        else:
            # Already in 24-hour format, just remove any extra spaces
            formatted_time = formatted_time.replace(" ", "")
        
        # Create datetime string for Google Calendar
        formatted_datetime = f"{today} {formatted_time}"
        print(f"Formatted datetime: {formatted_datetime}")
        
        # Get the symptom summary from session
        symptom_summary = session.get('symptom_summary', 'No symptom analysis available.')
        
        # Extract initial symptoms reported
        initial_symptoms = "No initial symptoms reported"
        for msg in SYMPTOM_CONVERSATION:
            if isinstance(msg, HumanMessage) and "following symptoms:" in msg.content:
                initial_symptoms = msg.content
                break
        
        # Prepare a more detailed description for the calendar event
        event_description = f"""
Patient: {patient_email}
Appointment with: Dr. {doctor['name']} ({doctor['specialization']})
Time: {appointment_time}

----- INITIAL SYMPTOMS -----
{initial_symptoms}

----- SPECIALIST RECOMMENDATION -----
{symptom_summary}
        """
        
        # Schedule meeting with properly formatted time and enhanced description
        meeting_result = schedule_meet_with_notification(
            formatted_datetime, 
            doctor_email, 
            patient_email,
            event_description,
            uploaded_files
        )
        
        # Store appointment in session
        appointment = {
            'doctor_id': doctor_id,
            'doctor_name': doctor['name'],
            'doctor_specialization': doctor['specialization'],
            'appointment_time': appointment_time,
            'patient_email': patient_email,
            'symptom_summary': symptom_summary,
            'meet_link': meeting_result.get('meet_link', ''),
            'uploaded_files': uploaded_files
        }
        
        session['last_appointment'] = appointment
        
        return jsonify({
            'success': True,
            'doctor_name': doctor['name'],
            'doctor_specialization': doctor['specialization'],
            'appointment_time': appointment_time,
            'meet_link': meeting_result.get('meet_link', ''),
            'message': 'Appointment booked successfully!'
        })
        
    except Exception as e:
        print(f"Error booking appointment: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error booking appointment: {str(e)}'
        })

if __name__ == "__main__":
    app.run(debug=True, port=5000)