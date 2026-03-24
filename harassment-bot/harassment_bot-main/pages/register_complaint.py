# import os
# import streamlit as st
# from chatbot.harassment_bot import process_message
# from collections import Counter
# from langchain import hub
# from langchain_groq import ChatGroq
# from langchain_core.prompts import MessagesPlaceholder
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema import HumanMessage,SystemMessage
# from dotenv import load_dotenv
# load_dotenv()
# groq_api = os.getenv('GROQ_API_KEY')

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ('system','You are a helpful Asistant'),
#         MessagesPlaceholder('chat_history'),
#         ('human','{input}'),
#         MessagesPlaceholder('agent_scratchpad')
#     ]
# )
# llm = ChatGroq(model_name='Llama-3.3-70b-Versatile',groq_api_key = groq_api)


# chat_history = [("System", "Hello! Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?")]
# context = ""
# grievance_stage = 1 

# st.title("Griveance Bot")

# if 'student_id' not in st.session_state:
#     st.session_state.student_id = 'N210132'
    
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = chat_history

# if 'context' not in st.session_state:
#     st.session_state.context = context

# if 'grievance_stage' not in st.session_state:
#     st.session_state.grievance_stage = grievance_stage

# def submit_message():
#     user_input = st.session_state.input_message
#     if user_input:
       
#         st.session_state.chat_history.append(("User", user_input))
        
#         response, updated_history, updated_context, updated_stage, final_response = process_message(
#             user_input, st.session_state.chat_history, st.session_state.context, st.session_state.grievance_stage, llm, prompt)
        
#         st.session_state.chat_history = updated_history
#         st.session_state.context = updated_context
#         st.session_state.grievance_stage = updated_stage

#         if updated_stage == 0:
#             st.session_state.admin_display = st.markdown(final_response)
        
#         st.session_state.input_message = ""

# for i, (sender, message) in enumerate(st.session_state.chat_history):
#     if sender == "System":
#         if not i%2:
#             st.chat_message("assistant").write(message)  
#         else:
#             st.chat_message("user").write(message)
#     else:
#         if not i%2 : 
#             st.chat_message("assistant").write(message)
#         else:
#             st.chat_message("user").write(message)



# st.text_input("Enter your message", key="input_message", on_change=submit_message)


# rate_limit = 60 
# api_calls_counter = Counter()  

# import os
# import streamlit as st
# from chatbot.harassment_bot import process_message
# from collections import Counter
# from langchain import hub
# from langchain_groq import ChatGroq
# from langchain_core.prompts import MessagesPlaceholder
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema import HumanMessage,SystemMessage
# from dotenv import load_dotenv
# import re
# load_dotenv()
# groq_api = os.getenv('GROQ_API_KEY')

# import pandas as pd
# df = pd.read_csv('data.csv',on_bad_lines='skip')

# def validate_id(student_id):
    
#     pattern = r"^N\d{6}$"

#     s= re.match(pattern, student_id)

#     if(s is None):
#         return False 
#     return student_id.lower() in df['ID_No'].str.lower().values

# def find_name(student_id):
#     student_id_upper = student_id.upper()
#     if student_id_upper in df['ID_No'].values:
#         name = df.loc[df['ID_No'] == student_id_upper, 'Name'].values[0]
#         st.write(name)
#         return name
#     else:
#         return ""
    
# if "id_valid" not in st.session_state:
#     st.session_state.id_valid = False
# if "student_id" not in st.session_state:
#     st.session_state.student_id = None
# if "student_name" not in st.session_state:
#     st.session_state.student_name = ""

# if not st.session_state.id_valid:
#     with st.popover("Enter Your Id"):
#         st.markdown("Hello 👋")
#         student_id= st.text_input("What's your Id no?").upper()
#         if(student_id):
#             if validate_id(student_id):
#                 st.session_state.id_valid = True
#                 st.session_state.student_id = student_id
#                 st.session_state.student_name = find_name(student_id)
#                 st.rerun()
    
#     st.header('Enter Your ID Number To continue 👆🏼')
#     print(student_id)

# if(st.session_state.id_valid):    
    
#     username = st.session_state.student_name 
#     print(username)
#     if username is not None: # Assign user name from session state
#         sys_msg = "Hello! " + username +" Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?"
#     else:
#         sys_msg = "Hello! Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?"
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ('system','You are a helpful Asistant'),
#             MessagesPlaceholder('chat_history'),
#             ('human','{input}'),
#             MessagesPlaceholder('agent_scratchpad')
#         ]
#     )

#     llm = ChatGroq(model_name='Llama-3.3-70b-Versatile',groq_api_key = groq_api)

#     chat_history = [("System", sys_msg)]
#     context = ""
#     grievance_stage = 1 

#     st.title("Griveance Bot")

#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = chat_history

#     if 'context' not in st.session_state:
#         st.session_state.context = context

#     if 'grievance_stage' not in st.session_state:
#         st.session_state.grievance_stage = grievance_stage

#     def submit_message():
#         user_input = st.session_state.input_message
#         if user_input:
        
#             st.session_state.chat_history.append(("User", user_input))
            
#             response, updated_history, updated_context, updated_stage, final_response = process_message(
#                 user_input, st.session_state.chat_history, st.session_state.context, st.session_state.grievance_stage, llm, prompt)
            
#             st.session_state.chat_history = updated_history
#             st.session_state.context = updated_context
#             st.session_state.grievance_stage = updated_stage

#             if updated_stage == 0:
#                 st.session_state.admin_display = st.markdown(final_response)
            
#             st.session_state.input_message = ""


#     for i, (sender, message) in enumerate(st.session_state.chat_history):
#         if sender == "System":
#             if not i%2:
#                 st.chat_message("assistant").write(message)  
#             else:
#                 st.chat_message("user").write(message)
#         else:
#             if not i%2 : 
#                 st.chat_message("assistant").write(message)
#             else:
#                 st.chat_message("user").write(message)


#     st.text_input("Enter your message", key="input_message", on_change=submit_message)


#     rate_limit = 60 
#     api_calls_counter = Counter()
import os
import streamlit as st
from chatbot.harassment_bot import process_message
from collections import Counter
from langchain import hub
from langchain_groq import ChatGroq
from langchain_core.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import re
import smtplib
from email.mime.text import MIMEText
import random
import time
import pandas as pd

# # Load environment variables
load_dotenv()

# Initialize API and Email Configuration
groq_api = os.getenv('GROQ_API_KEY')
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# EMAIL_ADDRESS = "mname3212@gmail.com"  # Your email
# EMAIL_PASSWORD = "lwjx pyzk lsfm czoe"

# # Read the ID CSV for validation
df = pd.read_csv('data.csv', on_bad_lines='skip')

# # Helper function to send OTP
# def send_otp(email):
#     otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
#     otp_expiry = time.time() + 600  # OTP expires in 10 minutes

#     # Save OTP in session state
#     st.session_state[email] = {"otp": otp, "expiry": otp_expiry}

#     # Send OTP via email
#     try:
#         # Create email content
#         subject = "Your OTP Code"
#         body = f"Your OTP code is: {otp}. It is valid for 10 minutes."
#         msg = MIMEText(body)
#         msg["Subject"] = subject
#         msg["From"] = EMAIL_ADDRESS
#         msg["To"] = email

#         # Send email
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()  # Upgrade to secure connection
#             server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#             server.send_message(msg)
#             st.session_state.otp_sent = True
#         return True
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return False

# # Validate ID function
def validate_id(student_id):
    pattern = r"^N\d{6}$"
    s = re.match(pattern, student_id)
    if s is None:
        return False 
    return student_id.lower() in df['ID_No'].str.lower().values

# # Find Name by User ID
def find_name(student_id):
    student_id_upper = student_id.upper()
    if student_id_upper in df['ID_No'].values:
        name = df.loc[df['ID_No'] == student_id_upper, 'Name'].values[0]
        st.write(name)
        return name
    else:
        return ""

# # Initialize session state variables
# if "id_valid" not in st.session_state:
#     st.session_state.id_valid = False
# if "student_id" not in st.session_state:
#     st.session_state.student_id = None
# if "student_name" not in st.session_state:
#     st.session_state.student_name = ""
# if "email_valid" not in st.session_state:
#     st.session_state.email_valid = False

# # User ID input and validation
# if not st.session_state.id_valid:
#     with st.popover("Enter Your Id"):
#         st.markdown("Hello 👋")
#         student_id = st.text_input("What's your Id no?").upper()
        # if student_id:
        #     if validate_id(student_id):
        #         st.session_state.id_valid = True
        #         st.session_state.student_id = student_id
        #         st.session_state.student_name = find_name(student_id)
        #         st.rerun()
    
#     st.header('Enter Your ID Number To continue 👆🏼')

# # Email OTP Verification
# if not st.session_state.email_valid and st.session_state.id_valid:
#     email = st.session_state.student_id + "@rguktn.ac.in"
    
#     # Send OTP if not already sent
#     if not st.session_state.get('otp_sent', False):
#         success = send_otp(email)
#         if success:
#             st.success("OTP sent to your email!")
#         else:
#             st.error("Failed to send OTP.")
    
#     if st.session_state.get('otp_sent', False):
#         otp = st.text_input("Enter the OTP sent to your email", key="otp")

#         # Button to verify OTP
#         if st.button("Verify OTP"):
#             stored_otp = st.session_state.get(email)
#             if stored_otp:
#                 # Check if OTP is expired
#                 if time.time() > stored_otp['expiry']:
#                     st.error("OTP has expired. Please request a new one.")
#                 elif otp.isdigit() and int(otp) == stored_otp['otp']:
#                     st.success("Email verified successfully!")
#                     st.session_state.email_valid = True
#                     st.rerun()
#                     # Remove OTP after successful verification
#                     del st.session_state[email]
#                 else:
#                     st.error("Invalid OTP. Please try again.")
#             else:
#                 st.error("No OTP request found for this email.")

#         # Button to resend OTP
#         if st.button("Resend OTP"):
#             success = send_otp(email)
#             if success:
#                 st.success("OTP sent again to your email!")
#             else:
#                 st.error("Failed to resend OTP.")

# # Chatbot Interface after Email Verification
# if st.session_state.id_valid and st.session_state.email_valid:
    
#     un = st.session_state.student_name 
#     sys_msg = f"Hello! {un} Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?" if un else "Hello! Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?"
    
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ('system', 'You are a helpful Assistant'),
#             MessagesPlaceholder('chat_history'),
#             ('human', '{input}'),
#             MessagesPlaceholder('agent_scratchpad')
#         ]
#     )

#     llm = ChatGroq(model_name='Llama-3.3-70b-Versatile', groq_api_key=groq_api)
#     chat_history = [("System", sys_msg)]
#     context = ""
#     grievance_stage = 1 

#     st.title("Grievance Bot")

#     # Initialize session state for chat
#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = chat_history
#     if 'context' not in st.session_state:
#         st.session_state.context = context
#     if 'grievance_stage' not in st.session_state:
#         st.session_state.grievance_stage = grievance_stage

#     def submit_message():
#         user_input = st.session_state.input_message
#         if user_input:
#             st.session_state.chat_history.append(("User", user_input))
#             response, updated_history, updated_context, updated_stage, final_response = process_message(
#                 user_input, st.session_state.chat_history, st.session_state.context, 
#                 st.session_state.grievance_stage, llm, prompt, st.session_state.student_name, st.session_state.student_id)
#             st.session_state.chat_history = updated_history
#             st.session_state.context = updated_context
#             st.session_state.grievance_stage = updated_stage
#             if updated_stage == 0:
#                 st.session_state.admin_display = st.markdown(final_response)
#             st.session_state.input_message = ""

#     # Display chat history
#     for i, (sender, message) in enumerate(st.session_state.chat_history):
#         if sender == "System":
#             if i == 0:
#                 st.chat_message("assistant").write(message)  
#             else:
#                 st.chat_message("assistant").write(message)
#         else:
#             if not i % 2:
#                 st.chat_message("user").write(message)
#             else:
#                 st.chat_message("user").write(message)

#     # Input field for user message
#     st.text_input("Enter your message", key="input_message", on_change=submit_message)

# # Rate limiting and API call tracking (optional for tracking)
# rate_limit = 60
# api_calls_counter = Counter()

import streamlit as st
import random
import time
from email.mime.text import MIMEText
import smtplib

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "mname3212@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "lwjx pyzk lsfm czoe"  # Replace with your email password (use environment variables in production!)

# OTP Sending Function
def send_otp(email):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    otp_expiry = time.time() + 300  # OTP expires in 5 minutes

    # Save OTP and expiry in session state
    st.session_state["otp_details"] = {"otp": otp, "expiry": otp_expiry}

    try:
        # Create email content
        subject = "Your OTP Code"
        body = f"Your OTP code is: {otp}. It is valid for 5 minutes."
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Streamlit App


# Initialize session state variables
if "otp_sent" not in st.session_state:
    st.session_state["otp_sent"] = False
if "otp_verified" not in st.session_state:
    st.session_state["otp_verified"] = False
if "otp_details" not in st.session_state:
    st.session_state["otp_details"] = {}

if "id_valid" not in st.session_state:
    st.session_state.id_valid = False
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "email_valid" not in st.session_state:
    st.session_state.email_valid = False

if not st.session_state['otp_verified']:

    st.title("Login")
    st.write("### Welcome! Please log in below")
    with st.container():
        student_id = st.text_input("Enter your ID")
        if st.session_state["otp_sent"]:
            email = student_id + "@rguktn.ac.in"  # Replace with actual domain logic
            otp_input = st.text_input("Enter OTP", disabled=False)
        else:
            email = ""  # Email will only be defined once OTP is sent
            otp_input = st.text_input("Enter OTP", disabled=True)

        if st.button("Send OTP"):
            if student_id:
                if validate_id(student_id.upper()):
                    st.session_state.id_valid = True
                    st.session_state.student_id = student_id
                    st.session_state.student_name = find_name(student_id)
                    print(st.session_state.student_name)
                    email = student_id + "@rguktn.ac.in"  # Adjust to your email domain logic
                    success = send_otp(email)
                if success:
                    st.success("OTP sent to your email!")
                    st.session_state["otp_sent"] = True
                    st.rerun()
                else:
                    st.error("Failed to send OTP. Try again later.")
            else:
                st.error("Please enter a valid ID.")

        if st.session_state["otp_sent"] and st.button("Verify OTP"):
            otp_details = st.session_state["otp_details"]
            if otp_details:
                if time.time() > otp_details["expiry"]:
                    st.error("OTP has expired. Please request a new one.")
                    st.session_state["otp_sent"] = False  # Reset OTP state
                elif otp_input.isdigit() and int(otp_input) == otp_details["otp"]:
                    st.success("OTP verified successfully! Logging you in...")
                    st.session_state["otp_verified"] = True
                    st.rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
            else:
                st.error("No OTP request found. Please request a new one.")

if st.session_state["otp_verified"]:
    un = st.session_state.student_name 
    sys_msg = f"Hello! {un} Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?" if un else "Hello! Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?"
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a helpful Assistant'),
            MessagesPlaceholder('chat_history'),
            ('human', '{input}'),
            MessagesPlaceholder('agent_scratchpad')
        ]
    )

    llm = ChatGroq(model_name='Llama-3.3-70b-Versatile', groq_api_key=groq_api)
    chat_history = [("System", sys_msg)]
    context = ""
    grievance_stage = 1 

    st.title("Grievance Bot")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = chat_history
    if 'context' not in st.session_state:
        st.session_state.context = context
    if 'grievance_stage' not in st.session_state:
        st.session_state.grievance_stage = grievance_stage

    def submit_message():
        user_input = st.session_state.input_message
        if user_input:
            st.session_state.chat_history.append(("User", user_input))
            response, updated_history, updated_context, updated_stage, final_response = process_message(
                user_input, st.session_state.chat_history, st.session_state.context, 
                st.session_state.grievance_stage, llm, prompt)
            st.session_state.chat_history = updated_history
            st.session_state.context = updated_context
            st.session_state.grievance_stage = updated_stage
            if updated_stage == 0:
                st.session_state.admin_display = st.markdown(final_response)
            st.session_state.input_message = ""

    for i, (sender, message) in enumerate(st.session_state.chat_history):
        if sender == "System":
            if i == 0:
                st.chat_message("assistant").write(message)  
            else:
                st.chat_message("assistant").write(message)
        else:
            if not i % 2:
                st.chat_message("user").write(message)
            else:
                st.chat_message("user").write(message)

    st.text_input("Enter your message", key="input_message", on_change=submit_message)

    rate_limit = 60
    api_calls_counter = Counter()
    
