from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
groq_api = os.getenv('GROQ_API_KEY')



llm = ChatGroq(model_name='Llama-3.3-70b-Versatile',groq_api_key = groq_api)