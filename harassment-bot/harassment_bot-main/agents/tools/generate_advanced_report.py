from langchain.tools import tool
from langchain import LLMChain, PromptTemplate
import pymongo 
import pandas as pd
from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://saikiranpatnana:mayya143@saikiran.bdu0jbl.mongodb.net/?retryWrites=true&w=majority&appName=saikiran"
client=MongoClient(uri)
db=client.test
collection=db['harassment_register']
from markdown import markdown
import streamlit as st
from weasyprint import HTML
from gridfs import GridFS
from config import llm
import numpy as np
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class LevelExtractor(BaseModel):
    level_number: int = Field(description="Indicates the level number.")
structured_llm = llm.with_structured_output(LevelExtractor)

def extract_level(report: str) -> LevelExtractor:
    prompt_template = f"""
    You are an ai assistant tasked with extracting the level number about an incident from the given report.
    report: {report}
    Response Format:
    {{
        "level_number": 1/2/3/4
    }}
    """
    structured_response = structured_llm.invoke(prompt_template)
    return structured_response

def store_to_db(report):

        # Prepare messages for the assistant
        messages = [
            (
                "system",
                "You are a helpful assistant that convert givent text to a Markdown script accordingly",
            ),
            (report),
        ]
        # Invoke the LLM
        ai_msg = llm.invoke(messages)
        # Convert the LLM response to Markdow
        markdown_content = ai_msg.content
        html_content = markdown(markdown_content)

        # Generate the PDF
        pdf_path = "output.pdf"
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"PDF successfully saved to {pdf_path}")
        fs = GridFS(db)
        # Store the PDF into MongoDB
        with open(pdf_path, "rb") as pdf_file:
            pdf_id = fs.put(pdf_file, filename="output.pdf")
        print(f"PDF successfully stored in MongoDB with ID: {pdf_id}")
        tokens = []
        level = extract_level(report).level_number
        for record in collection.find():
            tokens.append(record['token'])
        while True:
            random_token = np.random.randint(1000)
            if(random_token not in tokens):
                if "token" not in st.session_state:
                    st.session_state["token"] = random_token             
                collection.insert_one({'student_id': st.session_state.student_id,'token' : random_token , 'pdf_id' : pdf_id, 'level': level, 'complaint' : report, 'reported_timestamp' : pd.Timestamp.now(), 'status':0})
            break
    
def get_generate_advanced_report(llm):
    
    @tool("Generate_Advanced_Report")
    def generate_advanced_report(context: str) -> str:
        """Generate a comprehensive final report based on the given context and the determined level of grievance."""
        prompt_template = PromptTemplate.from_template(
        """
        Generate a comprehensive and professional report based on the following details:
        Context: {context}

        Instructions for different levels of harassment:

        Level 1:
        - Minor harassment incidents that can be resolved through initial support and awareness.
        - Provide encouragement and resources (e.g., counseling services, student support groups).
        - Include policy explanations to address harassment concerns.
        - Unresolved cases should be monitored and escalated to Level 2 if needed.
        - Examples: Verbal abuse such as demeaning language or public humiliation, minor cyber harassment like excessive messaging.
        - Response time: Within a week.

        Level 2:
        - Moderate harassment incidents requiring intervention and prompt action to prevent escalation.
        - Provide targeted advice, support, and access to grievance cells or university authorities.
        - Notify relevant university staff for resolution assistance.
        - Examples: Bullying, inappropriate cyber harassment (e.g., sharing inappropriate content, hacking), or stalking (e.g., unsolicited gifts).
        - Response time: Within 3 to 7 days.

        Level 3:
        - Serious harassment incidents requiring immediate intervention and support for affected students.
        - Report to higher university authorities and grievance committees.
        - Collect additional details to provide advisory and escalate as required.
        - Examples: Sexual harassment involving coercive requests or unwelcome touching, stalking involving monitoring movements, or significant discriminatory actions.
        - Response time: Immediate internal resolution.

        Level 4:
        - Severe harassment incidents involving violence, threats, or significant abuse of authority.
        - Requires urgent attention, escalation to university leadership, and involvement of legal or external authorities.
        - Gather detailed information from victims, witnesses, and faculty for legal reporting.
        - Examples: Sexual harassment with physical violence, stalking with malicious intent, abuse of authority involving physical threats, or discrimination with violence.
        - Response time: Immediate/urgent resolution.

        The report should include the following sections:
        1. Summary of the incident
        2. Date, time, and location of the incident
        3. Detailed description of the incident
        4. People involved (victims, witnesses, aggressors)
        5. Analysis of how the situation made the student feel
        6. Screening for violence and immediate danger
        7. Categorization of the harassment
        8. Recommendations for the student (e.g., support services, relevant authorities)
        9. Follow-up actions and response timeline
        10. Final recommendations and next steps

        Ensure the report is written professionally, emphasizes anonymity and safety, and addresses all necessary details to support the student and provide a thorough analysis for university authorities.
        """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt_template)
        final_report = chain.run(context=context) 
        store_to_db(final_report)
        return final_report
    
    return generate_advanced_report

