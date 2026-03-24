import pandas as pd
import warnings as warn
from IPython.display import display, Audio
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import logging
import os
import os
import time
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
save_dir = "images/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
warn.filterwarnings("ignore")
from sklearn.preprocessing import LabelEncoder
import joblib
from langchain_core.pydantic_v1 import BaseModel, Field
import warnings as warn
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Optional
import os
from langchain_groq import ChatGroq
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError('Set GROQ_API_KEY before running this project.')
os.environ['GROQ_API_KEY'] = groq_api_key
llm = ChatGroq(model_name='gemma2-9b-it', api_key=groq_api_key) 
 

def get_base_model_prediction(input: list):
  cols = list(pd.read_csv('train.csv').columns)[1:-1]
  input_vector  = list()
  for col in cols:
    if col in input:
      input_vector.append(1)
    else:
      input_vector.append(0)
  model = joblib.load('disease_prediction_model.pkl')
  lenc = joblib.load('label_encoder.pkl')
  print(input_vector)
  result = model.predict([pd.Series(input_vector)])
  result = lenc.inverse_transform([result])[0]
  return result

def get_insights_of_disease(result: str):
    precautions = pd.read_csv("M/precautions_df.csv")
    workout = pd.read_csv("M/workout_df.csv")
    description = pd.read_csv("M/description.csv")
    medications = pd.read_csv('M/medications.csv')
    diets = pd.read_csv("M/diets.csv")
    description = description[description['Disease'] == result]['Description']
    description = " ".join([w for w in description])

    precautions = precautions[precautions['Disease'] == result][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    precautions = [col for col in precautions.values]
    
    precautions = precautions[0].tolist()

    medication = medications[medications['Disease'] == result]['Medication']
    medication = [med for med in medication.values]
    medication = medication[0].strip('[]').split(',')
    medication = [item.strip().strip("'").strip('"') for item in medication]
    
    diet = diets[diets['Disease'] == result]['Diet']
    diet = [die for die in diet.values]
    diet = diet[0].strip('[]').split(',')
    diet = [item.strip().strip("'").strip('"') for item in diet]
    
    workouts = workout[workout['disease'] == result] ['workout']
    
    return description, precautions, medication, workouts, diet

class MedicalDoctorAnalysis(BaseModel):
    doctors_to_consult: list = Field(..., description="It has the list of doctors that can help with the treatment of the disease.")

def get_medical_doctor_analysis(disease_name: str) -> MedicalDoctorAnalysis:
    structured_llm = llm.with_structured_output(MedicalDoctorAnalysis)
    prompt_template = f"""
    Disease Name: {disease_name}  # The name of the disease provided by the user.
    Your Task:
      - Read the disease name carefully.
      -generate a list of doctors specializations that can help with the treatment of the disease.
    Response Format:
      {{
        "doctors": Give the list of doctors specializations that can help with the treatment of the disease.
      }}
    """
    structured_response = structured_llm.invoke(prompt_template)
    return structured_response.doctors_to_consult

class AyurvedicAnalysis(BaseModel):
    remedies: list[str] = Field(..., description="List of Ayurvedic remedies that can help with the treatment of the disease.")

def get_ayurvedic_analysis(disease_name: str) -> AyurvedicAnalysis:
    structured_llm = llm.with_structured_output(AyurvedicAnalysis)
    prompt_template = f"""
    Disease Name: {disease_name}
    
    Your Task:
      - Generate a simple list of general Ayurvedic remedies that can help with the treatment of the disease.
      - Each remedy should be a simple string, not a complex object.
      - Do not include descriptions or additional attributes.
    
    Response Format:
      {{
        "remedies": ["remedy1", "remedy2", "remedy3"]
      }}
    """
    structured_response = structured_llm.invoke(prompt_template)
    return structured_response

class MedicalAnalysis(BaseModel):
    disease_name: str = Field(..., description="Name of the disease predicted based on symptoms.")
    work_outs: list = Field(..., description="Give some physical excercises or activities beneficial for managing or recovering from the disease.")
    description: str = Field(..., description="Provide a brief description of the disease predicted in 2 lines.")
    precautions: list = Field(..., description="List the essential precautions or lifestyle changes that can help manage, mitigate, or prevent the disease. These can include hygiene practices, preventive measures, and activity restrictions.")
    diet: list = Field(..., description="Offer a diet plan or specific food recommendations to manage the disease. Include foods that are beneficial for the disease, as well as those that should be avoided to prevent aggravating symptoms.")
    doctors_to_consult: list = Field(..., description="Recommend the appropriate specialists or healthcare providers who should be consulted for further diagnosis and treatment. Include the type of doctor and their role in managing the disease (e.g., general practitioner, specialist).")
    medication: list = Field(..., description = "Based on the provided symptoms, suggest the appropriate medication.")

def get_medical_analysis(symptoms: list) -> MedicalAnalysis:
    structured_llm = llm.with_structured_output(MedicalAnalysis)
    prompt_template = f"""
    You are an AI healthcare assistant designed to analyze symptoms and provide medical insights. Please act like a doctor and use your knowledge to predict the disease based on the provided symptoms, and then offer the following information about the disease:
    Symptoms Provided:
        {symptoms}

    Your task:
    1. Disease Prediction: Based on the provided symptoms, predict the most likely disease the patient could be experiencing. Provide the disease name and a brief description of the disease, including its causes, risk factors, and common symptoms.

    2. Precautions to Take: Based on the predicted disease, suggest relevant precautions, lifestyle changes, or steps the patient can take to manage or prevent the disease.

    3. Diet Recommendations: Suggest a diet that can help manage the disease or improve the patient's condition. Be sure to include specific foods to include or avoid based on the disease.

    4. Doctors to Consult: Recommend the types of doctors or specialists that should

    Response Format:
      {{
        "disease_name": "Common Name of the disease predicted based on symptoms",
        "work_outs": Give some physical excercises or activities beneficial for managing or recovering from the disease."
        "description": "Provide a concise but detailed explanation of the disease, its causes, symptoms, and risk factors. Include how the disease is typically diagnosed and what to watch out for.",
        "precautions": "List the essential precautions or lifestyle changes that can help manage, mitigate, or prevent the disease. These can include hygiene practices, preventive measures, and activity restrictions.",
        "diet": "Offer a diet plan or specific food recommendations to manage the disease. Include foods that are beneficial for the disease, as well as those that should be avoided to prevent aggravating symptoms.",
        "doctors_to_consult": "Recommend the appropriate specialists or healthcare providers who should be consulted for further diagnosis and treatment. Include the type of doctor and their role in managing the disease (e.g., general practitioner, specialist).",
        "medication": "Based on the provided symptoms, suggest the appropriate medication."
      }}
    """
    result = structured_llm.invoke(prompt_template)
    print(result)
    return  result.disease_name, result.description, result.precautions, result.medication, result.work_outs, result.diet, result.doctors_to_consult


def get_image(disease:str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    query = f"Images of a person suffering from {disease}"
    response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
    soup = BeautifulSoup(response.content,"html.parser")
    image_tages = soup.find_all("img")
    del image_tages[0]
    image_data_mongo = []
    for i in image_tages:
        image_url =  i['src']
        return image_url
 