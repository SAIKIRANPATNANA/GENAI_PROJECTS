Collecting workspace information# MediAssist - AI-Powered Healthcare Triage Platform

MediAssist is an intelligent healthcare triage system that helps patients identify appropriate medical specialists based on their symptoms and facilitates remote consultations through video appointments.

![MediAssist Logo](https://img.icons8.com/color/96/000000/medical-doctor.png)

## Features

- **AI-powered Symptom Analysis**: Engage in a natural conversation about your symptoms using LangGraph agentic AI framework
- **Specialist Recommendation**: Get matched with the most appropriate medical specialist based on symptom analysis
- **Appointment Booking**: Schedule video consultations with recommended doctors
- **Medical Records Upload**: Securely share medical documents with your doctor
- **Google Calendar Integration**: Automatically receive Google Meet links for consultations
- **Email Notifications**: Get appointment confirmations and reminders via email
- **Detailed Medical Reports**: Receive comprehensive analysis of your symptoms

## Table of Contents

1. Installation
2. Configuration
3. Running the Application
4. Project Structure
5. Usage Guide
6. Technology Stack
7. AI Agent Architecture
8. Future Enhancements
9. Contributing
10. License

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/SAIKIRANPATNANA/TZ25_HAKATHON_MED_TRIAGE.git
   cd TZ25_HAKATHON_MED_TRIAGE
   ```

2. Create a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Email configuration (for sending appointment notifications)
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=your-app-password

# AI API keys
GROQ_API_KEY=your-groq-api-key

# Flask configuration
FLASK_APP=app.py
FLASK_DEBUG=1
```

### Google Calendar Integration (Optional)

To enable Google Calendar integration:

1. Set up a Google Cloud project and enable the Google Calendar API
2. Create OAuth 2.0 credentials and download them as credentials.json
3. Run the authentication script:
   ```bash
   python generate_token.py
   ```
4. Follow the browser prompts to authenticate and generate token.pickle

## Running the Application

Start the Flask server:

```bash
python app.py
```

The application will be available at http://127.0.0.1:5000/

## Project Structure

```
mediassist/
├── __pycache__/            # Python bytecode cache
├── agents.py               # LangGraph AI agents for symptom analysis
├── app.py                  # Main Flask application
├── credentials.json        # Google API credentials
├── flow.md                 # Project workflow documentation
├── flow.txt                # Detailed flow description
├── generate_token.py       # Google Calendar authentication
├── helper.py               # Helper functions
├── images/                 # Images directory
├── package.json            # Node.js dependencies
├── readme.md               # Project documentation
├── requirements.txt        # Python dependencies
├── static/                 # Static assets for web interface
│   └── images/             # UI image assets
├── tasks.py                # Task definitions for agent workflow
├── templates/              # HTML templates
│   ├── add_sym.html        # Symptom selection interface
│   ├── appointment_confirmation.html  # Booking confirmation
│   ├── book_appointment.html   # Doctor selection and booking
│   ├── home.html           # Landing page
│   ├── index.html          # Main index page
│   ├── loader.html         # Loading screen
│   ├── prediction.html     # Disease prediction results
│   ├── symptom_analysis.html   # Symptom chat interface
│   └── ... (other templates)
├── token.pickle            # Google API authentication token
├── tools.py                # Tool definitions for LangGraph agents
└── uploads/                # Directory for uploaded medical documents
```

## Usage Guide

### 1. Symptom Analysis

1. Open the application and navigate to "Symptom Analysis"
2. Enter your symptoms in the chat interface
3. The AI will ask relevant follow-up questions about:
   - Duration of symptoms
   - Associated symptoms
   - Exact location of symptoms
   - Frequency patterns
   - Triggers and severity
4. After sufficient information is gathered, you'll receive a specialist recommendation

### 2. Doctor Selection

1. Click "Book Appointment" after receiving a specialist recommendation
2. Browse available doctors matched to your needs
3. View doctor details including specialization, experience, languages, and fees
4. Select a doctor and choose an available time slot

### 3. Medical Record Upload

1. Upload any relevant medical records or test results
2. These will be shared securely with your doctor
3. Supported formats: PDF, DOC, DOCX, JPG, PNG

### 4. Appointment Confirmation

1. Enter your email address
2. Confirm your booking
3. Receive a Google Meet link for your video consultation
4. Get an email confirmation with appointment details

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Components**: 
  - LangChain - Framework for LLM applications
  - LangGraph - Agentic AI framework
  - Groq - LLM provider for fast inference
- **External APIs**: 
  - Google Calendar API - For scheduling appointments
  - Google Meet - For telehealth consultations
- **Email**: SMTP via Gmail for notifications
- **Data Storage**: Server-side session management

## AI Agent Architecture

MediAssist uses a multi-agent system built with LangGraph:

1. **Symptom Analysis Agent**:
   - Collects detailed information about reported symptoms
   - Asks follow-up questions to gather comprehensive data
   - Tracks conversation history for context awareness

2. **Medical Report Agent**:
   - Analyzes collected symptom data
   - Generates structured medical reports
   - Recommends appropriate medical specialists
   
3. **Tool Integration**:
   - Custom tools for symptom data structuring
   - Specialist matching algorithms
   - Appointment scheduling tools

The agents work together in a graph-based workflow, with state management ensuring coherent conversation flow.

## Future Enhancements

- Patient accounts and authentication
- Persistent storage of medical history
- Integration with electronic health record (EHR) systems
- Mobile application with push notifications
- Payment processing for consultations
- Follow-up appointment scheduling
- Prescription management system
- AI-powered medication recommendation
- Integration with pharmacy services
- Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This is a prototype application for demonstration purposes. For actual medical emergencies, please contact emergency services immediately.

Similar code found with 1 license type