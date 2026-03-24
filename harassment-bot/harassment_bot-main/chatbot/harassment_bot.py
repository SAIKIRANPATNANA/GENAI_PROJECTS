from agents.harassment_agent import generate_report
import pandas as pd
import streamlit as st
import numpy as np
from langchain_core.pydantic_v1 import BaseModel, Field
import google.generativeai as genai
from collections import Counter
from config import llm
from chatbot.collect_grievance_info import collect_harassment_info
import pymongo 
from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://saikiranpatnana:mayya143@saikiran.bdu0jbl.mongodb.net/?retryWrites=true&w=majority&appName=saikiran"
client=MongoClient(uri)
db=client.test
collection=db['harassment_register']
from markdown import markdown
from weasyprint import HTML
from gridfs import GridFS
# Intent Engines
# from intent_engine.determine_follow_up_or_final_response import determine_follow_up_or_final_response
# from intent_engine.determine_intent import determine_intent
# from intent_engine.determine_option import determine_option
# from intent_engine.process_navigation import classify_user_response_with_llm 

# UTILS
# from utils.query_vector_store import query_vector_store
# from utils.load_vector_stores import load_vector_stores
# from chatbot.collect_harassment_info import collect_harassment_info

chat_data = pd.DataFrame(columns=["Role", "Content"])

system_instructions = """
You are a University Harassment Reporting Chatbot. Your primary role is to assist students in reporting harassment incidents and provide a thorough summary of these reports to the relevant university authorities. Your purpose is to ensure students feel safe, supported, and heard while capturing the necessary information to analyze and address their grievances effectively.

As a virtual assistant, you greet students warmly, guide them through the process of reporting harassment, and create a supportive environment where they can share their concerns. After collecting the necessary information, you generate a detailed and categorized incident report for university authorities.

Your ultimate goal is to empower students to report incidents and contribute to a safer and more inclusive university environment. 
"""


messages = {
    "welcome_message": "Hello! Welcome to the Griviance Chatbot. How can I help you ?",
    "greet_user" : "Nice to meet you, {username}! How can I assist you today?",
    "ask_next_option": "Is this report covers the entire detail of the  harassment you have confronted with? Be Brave! Hope your issue will be resolve ASAP. You can track the status of you complaint using this token",
    "end_chat": "Thank you for using the Harassment Reporting Chatbot.Your report has been recorded anonymously, and your identity is protected. If you need further assistance or wish to report another incident, please feel free to reach out. We are here to support you and ensure your safety at all times.",
    "invalid_option": "I'm sorry, I didn't understand that. Can you please clarify."
}

def process_message(user_input, chat_history, context, harassment_stage, llm, prompt):
    global chat_data
    global username

    if False:
        response_text = messages["return_to_main_menu"]
        harassment_stage = 2  
    else:
        if harassment_stage == 0:
            response_text = messages["welcome_message"]
            harassment_stage = 1

        elif harassment_stage == 1:
            if False:
                pass
            else:
                harassment_stage = 3
                context += f"\n user-input:{user_input}"
                response = collect_harassment_info(context)
                if response.is_complete:
                    report = generate_report(response.collected_info)
                    # token = collection.find()
                    response_text = report + f"\n\n{messages['ask_next_option'].format(st.session_state.token)}"
                else:
                    response_text = response.next_question
                    harassment_stage = 3 
                harassment_stage = 13 
            harassment_stage = 3

        elif harassment_stage == 3:
            context += f"\n{user_input}"
            response = collect_harassment_info(context)
            if response.is_complete:
                report = generate_report(response.collected_info)
                print(report)
                response_text = report + f"\n\n{messages['ask_next_option']+f" {st.session_state.token}."}"
                harassment_stage = 13  
            else:
                response_text = response.next_question
                harassment_stage = 3 

        elif harassment_stage == 13:
            if user_input.lower() in ["yes", "y"]:
                response_text = messages["greet_user"].format(username=username)
                harassment_stage = 2 
            else:
                response_text = messages["end_chat"]
                harassment_stage = 0 
      
        

        print(context)

    # Update chat history
    chat_history.append(('System', response_text))


    return "", chat_history, context, harassment_stage, response_text
