from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm

class GrievanceResponse(BaseModel):
    is_complete: bool = Field(description="Indicates whether the information collected is complete.")
    next_question: str = Field(description="The next question to ask the user for collecting more information.")
    collected_info: str = Field(description="Collected information from the user so far.")

structured_llm = llm.with_structured_output(GrievanceResponse)

def collect_harassment_info(user_input: str) -> GrievanceResponse:
    prompt_template = f"""
    You are a guardian assistant tasked with collecting detailed information about a harassment incident from a university student. Your goal is to gather all necessary details in a friendly, supportive, and non-judgmental manner, ensuring the student feels safe and heard. Please avoid asking the same question multiple times and adapt based on the student's responses.

    User Input: {user_input}
    
    PLEASE COMMUNICATE WITH THE USER IN A FRIENDLY AND COMPASSIONATE MANNER.

    Task: Based on the context and user input, determine if the information collected is sufficient to generate a detailed incident report.
    If the information is complete, respond with is_complete as true and provide a summary of the collected information.
    If the information is not complete, respond with is_complete as false and provide the next question to ask the user to gather the required information.

    Ensure the collected information includes:
    - Description: Provide a clear and concise description of the incident (what happened).
    - Location: Where did the incident take place?
    - Date and Time: When did it occur?
    - Individuals Involved: Who were the people involved (e.g., victim, harasser, witnesses)?
    - Emotional Impact: How did the incident make the student feel (e.g., fear, anger, sadness)?
    - Danger/Injuries: Was anyone in danger? Describe any injuries or threatening actions.

    Response Format:
    {{
        "is_complete": true/false,
        "next_question": "string",
        "collected_info": "string"
    }}
    """

    structured_response = structured_llm.invoke(prompt_template)
    return structured_response