import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
from PIL import Image
import cv2
import io,os
import pymupdf
import json 
import requests
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.pydantic_v1 import BaseModel, Field
import warnings as warn
warn.filterwarnings("ignore")
from langchain_groq import ChatGroq
groq_api_key = os.getenv("GROQ_API_KEY")
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import pandas as pd
from ydata_profiling import ProfileReport
from matplotlib.patches import Rectangle
from google.cloud import vision
from google.api_core.exceptions import GoogleAPICallError
import sqlite3

langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials

nutrient_api_key = os.getenv("NUTRIENT_API_KEY")

def make_chatgroq(model_name):
    return ChatGroq(model_name=model_name, groq_api_key=groq_api_key)

llm = make_chatgroq('deepseek-r1-distill-llama-70b')

DB_PATH = 'blood_reports.db'

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)[1]
    processed_path = "uploads/preprocessed.jpg"
    cv2.imwrite(processed_path, image)
    return processed_path


def compress_image(input_path, output_path, quality=85, max_size=(800, 800)):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.thumbnail(max_size)
        img.save(output_path, "JPEG", quality=quality)
        print(f"Image compressed and saved at: {output_path}")

def get_parsed_text_using_tesseract(image_path):
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text

def get_parsed_text_using_pypdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    extracted_text = "\n".join([doc.page_content for doc in documents])
    return extracted_text

def is_scanned_pdf(file_path):
    doc = pymupdf.open(file_path)
    for page in doc:
        text = page.get_text("text")
        if text.strip():  
            return False
        if page.get_images(full=True):  
            return True 
    return True

def get_parsed_text_using_google_vision(image_path):
    try:
        client = vision.ImageAnnotatorClient()
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        if texts:
            extracted_text = texts[0].description
            return extracted_text
        else:
            print("No text found in image.")
    except GoogleAPICallError as e:
        print(e)
    except Exception as e:
        print(e)

def get_parsed_text_from_scanned_pdf(file_path):
    if not nutrient_api_key:
        raise RuntimeError("NUTRIENT_API_KEY is not set")
    response = requests.request(
    'POST',
    'https://api.nutrient.io/build',
    headers = {
        'Authorization': f'Bearer {nutrient_api_key}'
    },
    files = {
        'scanned': open(file_path, 'rb')
    },
    data = {
        'instructions': json.dumps({
        'parts': [
            {
            'file': 'scanned'
            }
        ],
        'actions': [
            {
            'type': 'ocr',
            'language': 'english'
            }
        ]
        })
    },
    stream = True
    )
    if response.ok:
        with open(file_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8096):
                fd.write(chunk)
    else:
        print(response.text)
        exit()
def generate_parsed_multi_report(llm, parsed_text):
    class MultiReportSummary(BaseModel):
        ehr: str = Field(..., description="Formatted markdown text summarizing the report.")
        lab_results: dict = Field(..., description="Structured JSON containing only abnormal test results.")
    def parse_multi_report(llm, parsed_text: str) -> MultiReportSummary:
        try:
            structured_llm = llm.with_structured_output(MultiReportSummary)
            prompt_template = f"""
            Given the following extracted blood report text containing multiple test reports:

            {parsed_text}

            Your Task:

            1. Extract patient information, lab details, and medical personnel information.
            2. List all tests conducted in markdown format with results.
            3. Identify abnormalities and highlight them separately, flagging each as either "Low" or "High" based on reference ranges.
            4. Generate two structured outputs:
            - A detailed markdown summary of the full report.
            - A separate JSON dictionary containing only abnormal parameters.
            5. Make sure you always generate a detailed, comprehensive and an eleborative electronic health report individually for each and every test included in this multitest parsed report text.
            
            Markdown Format Output Example:

            Patient Information:
            - Name: John Doe
            - Age: 45
            - Gender: Male
            - Patient ID: 12345
            - Sample Collected At: XYZ Lab

            Lab Information:
            - Lab Name: ABC Diagnostics
            - Address: 123 Street, City
            - Contact: +91 9876543210
            - Instruments Used: Automated Hematology Analyzer

            Medical Personnel:
            - Technician: Jane Smith
            - Pathologists:
            - Dr. A. Kumar (MD Pathology)
            - Dr. B. Sharma (MD Pathology)

            Conducted Tests & Results:
            --Complete Blood Count (CBC):
            - Hemoglobin: 12.5 g/dL _(Normal)_
            - WBC Count: 9,000 /µL _(Normal)_
            - Platelet Count: 150,000 /µL _(Low)_
            - Liver Function Test
            - SGPT: 75 U/L _(High)_
            - Bilirubin: 0.8 mg/dL _(Normal)_
            //like wise for all the tests present in the parsed text.

            Abnormal Parameters JSON Format:

            {{
            "lab_results": {{
                "Platelet Count": {{
                "value": "150000",
                "unit": "/µL",
                "reference_range": "150000 - 410000",
                "status": "Low"
                }},
                "SGPT": {{
                "value": "75",
                "unit": "U/L",
                "reference_range": "0 - 50",
                "status": "High"
                }}
            }}
            }}

            Guidelines for Accuracy:

            1. Classification of Abnormalities:
            - Compare each result with its reference range.
            - Flag as "Low" if the value is below the lower limit.
            - Flag as "High" if the value is above the upper limit.
            - If the value is within the range, mark it as "Normal".
            2. Grouping Results:
            - If a test name appears multiple times, group all results under one section.
            3. No Assumptions:
            - Do not assume "Normal" or "Abnormal" without numerical comparison.
            4. Output Format:
            - Return only valid markdown for the summary and structured JSON for abnormalities.

            Output Format:

            {{
            "ehr": "Formatted markdown text",
            "lab_results": {{
                "Parameter Name": {{
                "value": "Result Value",
                "unit": "Unit of Measurement",
                "reference_range": "Lower Limit - Upper Limit",
                "status": "Low/High/Normal"
                }}//like wise for all abnormal parameters
            }}
            }}
            """ 
            structured_response = structured_llm.invoke(prompt_template)
            return structured_response
        except Exception as e:
            print(e)
            llm = make_chatgroq('llama-3.3-70b-versatile')
            return parse_multi_report(llm,parsed_text)
    return parse_multi_report(llm, parsed_text)

def get_parsed_multi_report(file_path):
    parsed_mutli_report_text = get_parsed_text_using_gemini(file_path)
    llm = make_chatgroq('deepseek-r1-distill-llama-70b')
    parsed_multi_report = generate_parsed_multi_report(llm,parsed_mutli_report_text)
    return parsed_multi_report
def get_parsed_text_using_gemini(file_path):
    try: 
        # if("pdf" not in file_path):
        #     compressed_path = "uploads/compressed.jpg"
        #     compress_image(file_path, compressed_path, quality=70, max_size=(800, 800))
        #     file_path = compressed_path
        # raise Exception("Could not do!")
        # model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        file_id = genai.upload_file(path=file_path)
        user_input = """
        Extract the text from the uploaded blood report file!
        """
        response = model.generate_content([file_id, user_input])
        return response.text
    except Exception as e:
        print(e)
        print("Gemini Flash Failed!")
        case = 0
        try:
            if 'pdf' in file_path: 
                if(is_scanned_pdf(file_path)):
                    print(f"{file_path} a scanned document!")
                    get_parsed_text_from_scanned_pdf(file_path)
                return get_parsed_text_using_pypdf(file_path)
            else:
                case = 1
                processed_image = preprocess_image(file_path)
                return get_parsed_text_using_google_vision(processed_image)
        except Exception as e:
            print(e)
            if(not case):
                print("Pypdf Failed!")
                print("Nothing to do.")
            else: 
                print("Google Visison Failed!")
                processed_image = preprocess_image(file_path)
                return get_parsed_text_using_tesseract(processed_image)
def generating_structured_report(llm,parsed_text):
    class LabTestReport(BaseModel):
        patient_info: dict = Field(..., description="Basic details of the patient.")
        lab_info: dict = Field(..., description="Details about the laboratory.")
        test_name: str = Field(..., description="Name of the test performed.")
        lab_results: dict = Field(..., description="Structured representation of blood test results.")
        medical_personnel: dict = Field(..., description="Details of medical professionals who processed the report.")
    def generate_structured_report(llm,parsed_text: str) -> LabTestReport:
        try: 
            structured_llm = llm.with_structured_output(LabTestReport)
            """
            Converts extracted OCR text from a blood report into a structured JSON format.
            """
            prompt_template = f"""
            Given the following extracted blood report text:
            {parsed_text}

            Your Task:
                -Analyze the text carefully and extract relevant details into a structured format.  
                - Ensure accurate classification of test results:
                - Compare the extracted value numerically with the provided reference range.
                - Mark the status as:
                - "Low" if the value is below the lower limit of the reference range.
                - "High" if the value is above the upper limit of the reference range.
                - "Normal" if the value falls within the range.
                - If reference range data is missing or unclear, mark status as "Not Available" instead of assuming High or Low.
                - Make sure you correctly and appropriately classify the test name into any of the following:
                       -- Blood Group Test
                       -- Calcium Blood Test
                       -- Cholestrol And Lipid Test
                       -- C-reactive Protien Test
                       -- D-dimer Test
                       -- Erythrocyte Sedimentation Rate Test
                       -- Folate Test
                       -- Complete Blood Count Test
                       -- HbA1c Test
                       -- hCG Test
                       -- International Normalised Ratio Test
                       -- Iron Studies Blood Test
                       -- Kidney Function Test
                       -- Liver Function Test
                       -- Magnesium Blood Test
                       -- Oestrogen Blood Test
                       -- Prostate Specific Antigen Test
                       -- Testosterone Blood Test
                       -- Thyroid Function Test
                       -- Troponin Blood Test
                       -- Vitamin B12 Test
                       -- Vitamin D Test
            Response Format:
                 {{
            "patient_info": {{
                "name": "",  # Extract the patient's name
                "age": "",  # Extract the age
                "gender": "",  # Extract gender
                "patient_id": "",  # Extract patient ID if available
                "sample_collected_at": "",  # Extract sample collection location
                "referred_by": "",  # Doctor who referred the test
                "registered_on": "",  # Registration date
                "collected_on": "",  # Sample collection date
                "reported_on": ""  # Date when report was generated
            }},
            "lab_info": {{
                "lab_name": "",  # Extract lab name
                "lab_contact": {{
                "phone": "",  # Extract lab phone number if available
                "email": ""  # Extract lab email if available
                }},
                "lab_address": "",  # Extract full address of the lab
                "website": "",  # Extract website if available
                "instruments": "",  # Instruments used for testing
                "generated_on": ""  # Report generation date
            }},
            "test_name": "",  # Extract the test name,
            "lab_results": {{
                "param_name_1": {{
                    "value": "",  # Extract parameter value
                    "unit": "",  # Extract unit (e.g., g/dL, cells/cumm)
                    "reference_range": "",  # Extract reference range
                    "status": ""  # Indicate if value is Normal, High, or Low
                }},
                // Like this, extract all available test parameters in the report
            }},
            "medical_personnel": {{
                "medical_lab_technician": "",  # Extract name of lab technician
                "pathologists": [
                {{
                    "name": "",  # Extract name of pathologist
                    "qualification": ""  # Extract qualification (e.g., MD Pathology)
                }},
                {{
                    "name": "",  # Extract name of additional pathologist if available
                    "qualification": ""
                }}
                ]
            }}
            }}

            Important Instructions for Classification:
            - Always extract the reference range values as numbers.
            - Check for formatted errors in extracted data (e.g., "4.5-5.5" should be split into 4.5 and 5.5).
            - If reference range is missing, set "status": "Not Available" instead of assuming High/Low.
            - Avoid misclassifying values that fall exactly within the reference range (e.g., if `value = 3.5` and range is `1.5 - 4.1`, it should be marked as `"Normal"`).

            Return only valid JSON output.
            """
            structured_response = structured_llm.invoke(prompt_template)
            return structured_response
        except Exception as e:
            print(e)
            ehr = parsed_text
            llm = make_chatgroq('llama-3.3-70b-versatile')
            parsed_report = generate_structured_report(llm,ehr)
            return parsed_report
    return generate_structured_report(llm,parsed_text)

def get_parsed_report(file_path):
  ehr = get_parsed_text_using_gemini(file_path)
  llm = make_chatgroq('deepseek-r1-distill-llama-70b')
  parsed_report = generating_structured_report(llm,ehr)
  return parsed_report
  
COLORS = {
    'high': '#FF6B6B',
    'low': '#4ECDC4',
    'range_fill': '#A8E6CF',
    'range_line': '#3D84A8',
    'text': '#2C3E50',
    'grid': '#DAE1E7'
}

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

def convert_to_float(value_str):
    try:
        numeric_value = "".join([char for char in value_str if char.isdigit() or char == "."])
        return float(numeric_value)
    except ValueError:
        return None  

def create_blood_test_plots(parsed_report, output_folder="static/plots"):
    try:
        os.makedirs(output_folder, exist_ok=True)
        if hasattr(parsed_report, 'dict'):
            blood_results = parsed_report.dict()['lab_results']
        else:
            blood_results = parsed_report.lab_results
        abnormal_params = {k: v for k, v in blood_results.items() if v['status'] in ('High', 'Low')}
        for param, details in abnormal_params.items():
            try:
                value = convert_to_float(str(details['value']).strip())
                if value is None:
                    print(f"Skipping {param}: Cannot convert value '{details['value']}' to a number.")
                    continue  
                ref_range = details['reference_range'].strip()
                if '-' in ref_range:
                    lower, upper = map(convert_to_float, ref_range.split('-'))
                elif '–' in ref_range:  
                    lower, upper = map(convert_to_float, ref_range.split('–'))
                else:
                    print(f"Skipping {param}: Invalid range format - {ref_range}")
                    continue  
                if lower is None or upper is None:
                    print(f"Skipping {param}: Reference range values could not be converted.")
                    continue
                unit = details['unit']
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.patch.set_facecolor('white')
                ax.set_facecolor('#F8FBFF')
                rect = Rectangle((0.7, lower), 0.6, upper-lower,
                                 facecolor='#A8E6CF', alpha=0.3, label='Reference Range')
                ax.add_patch(rect)
                is_high = value > upper
                point_color = '#FF6B6B' if is_high else '#4ECDC4'
                for alpha in [0.1, 0.2, 0.3]:
                    ax.scatter(1, value, s=300 + (1-alpha)*200, color=point_color, alpha=alpha, zorder=4)
                ax.scatter(1, value, s=200, color=point_color, marker='o', edgecolor='white', linewidth=2, zorder=5, 
                           label=f"Result: {value} {unit}")
                if is_high:
                    ax.vlines(x=1, ymin=upper, ymax=value, colors=point_color, linestyles='--', alpha=0.6, linewidth=2)
                else:
                    ax.vlines(x=1, ymin=value, ymax=lower, colors=point_color, linestyles='--', alpha=0.6, linewidth=2)
                ax.set_xlim(0.5, 1.5)
                ax.set_ylim(min(lower * 0.9, value * 0.9), max(upper * 1.1, value * 1.1))
                ax.set_xticks([])
                for y in [lower, upper]:
                    ax.axhline(y=y, color='#3D84A8', linestyle='--', alpha=0.4, linewidth=2)
                for y, label in [(lower, 'Lower'), (upper, 'Upper')]:
                    ax.text(0.6, y, f'{label}: {y}', verticalalignment='bottom', horizontalalignment='right', 
                            fontsize=10, color='white', bbox=dict(facecolor='#3D84A8', alpha=0.7, pad=3, boxstyle='round,pad=0.5'))
                ax.grid(True, axis='y', linestyle=':', alpha=0.2, color='#DAE1E7')
                plt.title(f"{param} Test Result", pad=20, fontsize=16, fontweight='bold', color='#2C3E50')
                plt.ylabel(f"Value ({unit})", fontsize=12, color='#2C3E50')
                status_color = '#FF6B6B' if is_high else '#4ECDC4'
                status_text = 'HIGH' if is_high else 'LOW'
                bbox_props = dict(boxstyle="round,pad=0.5", fc=status_color, ec="white", alpha=0.8)
                plt.text(0.98, 0.02, status_text, transform=ax.transAxes, color='white', fontsize=12, fontweight='bold',
                         bbox=bbox_props, horizontalalignment='right', verticalalignment='bottom')
                legend = plt.legend(loc="upper right", fontsize=10, framealpha=0.95, shadow=True)
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_edgecolor('#3D84A8')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#3D84A8')
                    spine.set_linewidth(1.5)
                plt.tight_layout()
                save_path = os.path.join(output_folder, f"{param.replace(' ', '_')}.png")
                plt.savefig(save_path, bbox_inches="tight", dpi=300, facecolor='white', edgecolor='none')
                plt.close()
                print(f"Successfully created plot for {param}")
            except Exception as param_error:
                print(f"Error creating plot for {param}: {str(param_error)}")
                continue
    except Exception as e:
        print(f"Error in create_blood_test_plots: {str(e)}")
        raise Exception(f"Failed to create plots: {str(e)}")


def get_medical_insights_n_recommendataions(parsed_report):
  class ParameterRecommendation(BaseModel):
      parameter: str = Field(..., description="Name of the abnormal blood test parameter.")
      status: str = Field(..., description="Indicates whether the parameter is high or low.")
      possible_disease: list = Field(..., description="Possible health effects.")
      possible_causes: list = Field(..., description="Possible reasons for the abnormality.")
      dietary_suggestions: list = Field(..., description="Recommended foods to normalize levels.")
      lifestyle_changes: list = Field(..., description="Exercise, hydration, and other lifestyle recommendations.")
      medical_advice: str = Field(..., description="When to consult a doctor or take further medical action.")
  class HealthInsights(BaseModel):
      abnormal_parameters: list[ParameterRecommendation] = Field(..., description="List of insights for all abnormal parameters.")
  llm = ChatGroq(model_name='deepseek-r1-distill-llama-70b',groq_api_key = groq_api_key)
  structured_llm = llm.with_structured_output(HealthInsights)
  def generate_health_recommendations_n_insights(llm,abnormal_results: dict):
    try:
        if len(abnormal_results) == 0: 
            return {}
        """
        Generates insights & recommendations for all abnormal blood parameters in a single call.
        """
        formatted_params = "\n".join([f"- {param}: {status}" for param, status in abnormal_results.items() if status == 'Low' or status=='High'])
        print("--------------------------------")
        print("Formatted Abnormal Parameters")
        print(formatted_params)
        print("--------------------------------")

        prompt_template = f"""
            The following blood test parameters are abnormal:
            {formatted_params}

            Your Task:
            For each abnormal parameter, generate structured health insights based on medical knowledge relevant to India, considering:  
            - Common health conditions prevalent in India (e.g., anemia, diabetes, hypertension).  
            - Dietary recommendations using locally available foods.  
            - Lifestyle suggestions that are practical for Indian demographics.  
            - Medical advice aligned with healthcare practices in India.  

            Response Format:
            {{
            "abnormal_parameters": [
                {{
                "parameter": "Parameter Name",
                "status": "High/Low",
                "possible_disease": ["List possible health conditions relevant to India"],
                "possible_causes": ["List of possible reasons"],
                "dietary_suggestions": ["Indian foods that help normalize levels (e.g., spinach for iron deficiency)"],
                "lifestyle_changes": ["Exercise, hydration, and habits suited to Indian lifestyles"],
                "medical_advice": "When to consult a doctor? Consider India's healthcare access & common medical practices."
                }}
            ]
            }}

            Additional Guidelines:
            - Dietary suggestions must include Indian foods (e.g., "Turmeric and cumin for anti-inflammatory benefits").  
            - Lifestyle changes should be practical for Indian work-life routines (e.g., "Yoga for stress management").  
            - Medical advice should consider India's healthcare accessibility (e.g., "Consult a general physician at a government clinic if symptoms persist").  

            Return only valid JSON output.
            """
        structured_response = structured_llm.invoke(prompt_template)
        return structured_response.dict()
    except Exception as e:
        print(e)
        llm = make_chatgroq('llama-3.3-70b-versatile')
        return generate_health_recommendations_n_insights(llm, abnormal_results)
  blood_results = parsed_report.lab_results
  abnormal_results = abnormal_results = {param: details['status'] for param, details in blood_results.items() if details['status'] != "Normal"}
  recommendations_n_insights = generate_health_recommendations_n_insights(llm,abnormal_results)
  return recommendations_n_insights
 
def get_patient_report_history(patient_name, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("User Id: ", user_id)
    print("Patient Name: ", patient_name)
    query = """
    SELECT uploaded_at, parsed_report
    FROM Reports
    WHERE patient_id in (select patient_id FROM Patients WHERE name = ? AND user_id = ?)
    ORDER BY uploaded_at ASC;
    """
    cursor.execute(query, (patient_name, user_id))
    reports = cursor.fetchall()
    conn.close()
    print("Reports Count:", len(reports))
    if not reports:
        return "No previous reports available."
    formatted_reports = [{"generated_on": json.loads(parsed_report)['lab_info']['generated_on'],  
                         "test_name": json.loads(parsed_report)['test_name'],
                         "lab_results": json.loads(parsed_report)['lab_results']} 
                        for date, parsed_report in reports]
    print("Formatted Reports Count:", len(formatted_reports))
    return formatted_reports[:-1]

message_store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in message_store:
        message_store[session_id] = ChatMessageHistory()
    return message_store[session_id]

def get_chat_response(message: str, role: str, current_report: dict, previous_reports=None, session_id="chat1"):
    print("Previous Reports:", previous_reports)
    print("Previous Reports Count:", len(previous_reports))
    system_prompt = """
    You are a knowledgeable and helpful medical assistant, analyzing blood test reports.

    User Role: {role}
    Doctor - Provide technical, clinical explanations using medical terminology.
    Patient - Use simple, easy-to-understand language without medical jargon.

    Available Data:
    Current Report:  
    {current_report}  

    Previous Reports:  
    {previous_reports} (Use for comparison when applicable or asked for)

    Guidelines for Response Generation:
    - Keep responses concise and to the point.  
    - If previous reports exist, compare trends and highlight key changes.  
    - Explain the clinical significance of any abnormalities.  
    - Provide insights into overall health status based on the report.  
    - Suggest appropriate follow-up actions:  
    - Dietary and lifestyle modifications  
    - Possible medical interventions  
    - When to consult a doctor  

    If any data is unclear or missing, mention it explicitly instead of assuming values.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    model = ChatGroq(model="gemma2-9b-it", groq_api_key=groq_api_key)
    chain = (
        RunnablePassthrough.assign(
            current_report=lambda x: x["current_report"],
            previous_reports=lambda x: x["previous_reports"],
            role=lambda x: x["role"]
        )
        | prompt
        | model
    )
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )
    user_message = HumanMessage(content=message)
    try:
        response = with_message_history.invoke(
            {
                "current_report": current_report,
                "previous_reports": previous_reports or "No previous reports available.",
                "messages": [user_message],
                "role": role,
            },
            config={"configurable": {"session_id": session_id}},
        )
        return response.content
    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."

def get_patient_names_from_db_wrt_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select distinct name from Patients where user_id  = ?", (user_id,)) 
    patient_names = cursor.fetchall()
    conn.close()
    patient_names =  [patient_name[0] for patient_name in patient_names if len(patient_name)]
    return patient_names

def get_report_ids_n_test_names(patient_name, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT report_id, json_extract(parsed_report, '$.test_name') 
        FROM Reports 
        WHERE patient_id IN (
            SELECT patient_id 
            FROM Patients 
            WHERE user_id = ? AND name = ?
        )
    """, (user_id, patient_name))
    reports = cursor.fetchall()
    conn.close()
    return reports

def grouping_test_names(test_names):
    llm = ChatGroq(model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
    class TestGroup(BaseModel):
        standardized_test_name: str = Field(..., description="Unique standardized test name.")
        report_ids: list[int] = Field(..., description="List of report IDs associated with this test name.")
    class TestGroupingOutput(BaseModel):
        grouped_tests: list[TestGroup] = Field(..., description="List of grouped test names and their report IDs.")
    def group_test_names_with_llm(llm,test_names):
        try:
            structured_llm = llm.with_structured_output(TestGroupingOutput)
            formatted_test_names = "\n".join([f"- {t} (Report ID: {rid})" for rid, t in test_names])

            prompt_template = f"""
            You are an intelligent medical assistant responsible for grouping blood test names.

            The following test names were extracted from a patient's reports, along with their respective report IDs:
            {formatted_test_names}

            Your task:
            - Group test names that refer to the same medical test.
            - Ensure that each standardized test name includes only the provided report IDs.
            - Return a structured JSON output with standardized test names mapped to their corresponding report IDs.

            Expected JSON Output Format:
            {{
                "grouped_tests": [
                    {{
                        "standardized_test_name": "Hemoglobin",
                        "report_ids": [1,2,3]
                    }},
                    {{
                        "standardized_test_name": "Liver Function Test",
                        "report_ids": [40, 41]
                    }}
                ]
            }}

            Important:  
            - Maintain accurate mapping between standardized test names and report IDs.
            - Ensure that no report IDs are missing or incorrectly reassigned.
            - Do not add extra test names or modify the provided report IDs.

            Return only a valid JSON response.
            """ 

            structured_response = structured_llm.invoke(prompt_template)
            return structured_response.dict() 
        except Exception as e:
            print(e)
            try:
                llm = make_chatgroq("gemma2_9b_it")
                return group_test_names_with_llm(llm,test_names)
            except Exception as e:
                print(e)
                llm = make_chatgroq("deepseek-r1-distill-qwen-32b")
                return group_test_names_with_llm(llm,test_names)
    return group_test_names_with_llm(llm,test_names)


def get_lab_results_for_test(report_ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"""
        SELECT report_id, json_extract(parsed_report, '$.lab_results')
        FROM Reports 
        WHERE report_id IN ({",".join(["?"] * len(report_ids))})
    """
    cursor.execute(query, report_ids)
    results = cursor.fetchall()
    conn.close()
    lab_results = {str(report_id): json.loads(data) for report_id, data in results if data}
    return lab_results  

def standardizing_param_names_with_llm(lab_results):
    class StandardizedParameter(BaseModel):
        original_name: str = Field(..., description="Original test name.")
        standardized_name: str = Field(..., description="Unified standard test name.")
    class StandardizedLabResults(BaseModel):
        standardized_tests: list[StandardizedParameter] = Field(..., description="List of standardized lab test parameters.")
    llm = ChatGroq(model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
    def standardize_param_names_with_llm(llm,lab_results):
        try:
            structured_llm = llm.with_structured_output(StandardizedLabResults)
            test_param_names = list({param for report in lab_results.values() for param in report.keys()})
            prompt_template = f"""
            The following blood test parameter names were extracted:
            {test_param_names}

            Your task:
            - Standardize each parameter name to a commonly accepted medical term.
            - Return a structured JSON mapping the original test name to the standardized name.

            Example Output:
            {{
                "standardized_tests": [
                {{
                    "original_name": "Hb",
                    "standardized_name": "Hemoglobin"
                }},
                {{
                    "original_name": "WBC Count",
                    "standardized_name": "White Blood Cell Count"
                }},
                {{
                    "original_name": "HB",
                    "standardized_name": "Hemoglobin"
                }}
                ]
            }}
            """
            structured_response = structured_llm.invoke(prompt_template)
            return structured_response.dict()
        except Exception as e:
            print(e)
            try:
                llm = make_chatgroq("gemma2_9b_it")
                return standardize_param_names_with_llm(llm,lab_results)
            except Exception as e:
                print(e)
                llm = make_chatgroq("deepseek-r1-distill-qwen-32b")
                return standardize_param_names_with_llm(llm,lab_results)
    return standardize_param_names_with_llm(llm,lab_results)       

def apply_standardized_names(lab_results, standardization_map):
    standardized_results = []
    for report_id, tests in lab_results.items():
        standardized_report = {"report_id": report_id}
        for param, details in tests.items():
            standardized_name = next((item["standardized_name"] for item in standardization_map["standardized_tests"] if item["original_name"] == param), param)
            standardized_report[standardized_name] = details["value"]
        standardized_results.append(standardized_report)
    return pd.DataFrame(standardized_results)

def generate_pandas_profiling_report(df, report_path):
    if df.empty:
        print("No data available for profiling")
        return None
    try:
        df.set_index('report_id')
        profile = ProfileReport(df, explorative=True)
        profile.to_file(report_path)
    except Exception as e:
        print(f"Error generating profiling report: {e}")
        return None

def plot_scatter(df, selected_param):
    print(f"Plotting scatter for param: {selected_param}")
    print(f"DataFrame info: {df.info()}")
    print(f"DataFrame head: \n{df.head()}")
    if df.empty or selected_param not in df.columns:
        print(f"No data available for {selected_param}")
        return None
    plots_dir = os.path.join("static", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    plt.figure(figsize=(10, 5))
    df_sorted = df.sort_values('uploaded_at')
    plt.plot(df_sorted['uploaded_at'], df_sorted[selected_param], '-', color='blue', alpha=0.5)
    plt.scatter(df_sorted['uploaded_at'], df_sorted[selected_param], color='blue', alpha=0.7, label=selected_param)
    plt.xlabel('Upload Date')
    plt.ylabel(f'{selected_param} Value')
    plt.title(f'Trend of {selected_param} Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    safe_param = selected_param.replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_param = ''.join(c for c in safe_param if c.isalnum() or c in '_-')
    plot_path = os.path.join("plots", f"{safe_param}_trend.png")  
    full_path = os.path.join("static", plot_path) 
    plt.savefig(full_path, bbox_inches="tight", dpi=300)
    plt.close()
    return plot_path  

def get_uploaded_timestamps(report_ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"""
        SELECT report_id, uploaded_at
        FROM Reports 
        WHERE report_id IN ({",".join(["?"] * len(report_ids))})
    """
    cursor.execute(query, report_ids)
    results = cursor.fetchall()
    conn.close()

    return pd.DataFrame(results, columns=["report_id", "uploaded_at"])

def merge_uploaded_timestamps(df):
    timestamps_df = get_uploaded_timestamps(df["report_id"].tolist())
    if "report_id" in df.columns:
        df = df.merge(timestamps_df, on="report_id", how="left")
    return df
