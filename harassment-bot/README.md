# Harassment-Bot

A Gen AI-Based Chat Bot for Addressing Complaints Regarding Women Harassment in Universities.

## **Overview**
Harassment-Bot is an AI-powered chatbot designed to provide a secure and streamlined platform for addressing and tracking complaints related to women's harassment in educational institutions.

## **Features**
- **AI Chatbot**: Handles user queries and complaints seamlessly.
- **Complaint Tracking**: Allows users to track the status of their complaints using a unique token.
- **Admin Dashboard**: Enables authorized administrators to manage complaints and update statuses.
- **PDF Upload and Download**: Complaints can be uploaded as PDFs, and users can download their registered complaint details.

---

## **Steps to Set Up the Application**

### **1. Clone the Repository**
```bash
git clone <repository_url>
cd harassment_bot
```

### **2. Create a Conda Environment**
```bash
conda create -n harassment -y
conda activate harassment
```

### **3. Install Required Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
```bash
streamlit run main.py
```

---

## **How to Use**

### **For Users**
1. **Register Complaint**: Use the chatbot to register your complaint with all necessary details.
2. **Track Complaint**: Enter your registered token number in the "Track Complaint Status" section to check the progress of your complaint.

### **For Admins**
1. **Log In**: Access the admin dashboard using your credentials.
2. **Manage Complaints**: View, edit, and update complaint statuses.
3. **Download Complaints**: Retrieve and download complaints in PDF format for documentation.

---

## **Project Structure**
```
harassment_bot/
├── main.py                     # Entry point of the application
├── pages/                      # Contains Streamlit pages
│   ├── admin_login.py          # Admin login and dashboard functionality
│   ├── track_complaint_status.py # Track complaint status functionality
├── requirements.txt            # List of required Python packages
├── README.md                   # Project documentation
├── data/                       # Placeholder for additional resources (if any)
```

---

## **Technologies Used**
- **Python**: Backend logic and API handling.
- **Streamlit**: Web application framework for a user-friendly interface.
- **MongoDB**: Database for secure and scalable data storage.
- **GridFS**: Handles PDF uploads and retrievals.

---

## **Future Enhancements**
- **Multi-language Support**: Enable chatbot interaction in multiple languages.
- **Enhanced Security**: Implement advanced encryption techniques for complaint data.
- **Analytics Dashboard**: Provide detailed reports and analytics for administrators.

---

## **Contributing**
We welcome contributions! Please fork the repository, create a branch, and submit a pull request with your proposed changes.

---

## **License**
This project is licensed under the [MIT License](LICENSE).

---

## **Contact**
For any questions or feedback, please contact us at [n210782@rguktn.ac.in] & [n210132@rguktn.ac.in]
