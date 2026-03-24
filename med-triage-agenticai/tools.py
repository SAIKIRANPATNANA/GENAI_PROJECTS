from typing import List, Dict, Any
from langchain_core.tools import Tool

# @tool
# def get_symptom_details_tool(symptom: str) -> str:
#     """
#     Get detailed information about a specific symptom.
    
#     Args:
#         symptom: The name of the symptom to get details for.
        
#     Returns:
#         A prompt asking for more information about the symptom.
#     """
#     return f"I need more information about your {symptom}. Could you describe it in more detail?"

# @tool
# def get_symptom_duration_tool(symptom: str) -> str:
#     """
#     Inquire about how long a patient has been experiencing a symptom.
    
#     Args:
#         symptom: The name of the symptom to inquire about.
        
#     Returns:
#         A prompt asking about symptom duration.
#     """
#     return f"How long have you been experiencing {symptom}? (days, weeks, months?)"

# @tool
# def get_symptom_severity_tool(symptom: str) -> str:
#     """
#     Ask about the severity of a symptom on a scale of 1-10.
    
#     Args:
#         symptom: The name of the symptom to inquire about.
        
#     Returns:
#         A prompt asking about symptom severity.
#     """
#     return f"On a scale of 1-10, how severe would you say your {symptom} is? (1 being barely noticeable, 10 being the worst pain/discomfort imaginable)"

# @tool
# def get_symptom_location_tool(symptom: str) -> str:
#     """
#     Ask about the specific location or region of the body where a symptom is experienced.
    
#     Args:
#         symptom: The name of the symptom to inquire about.
        
#     Returns:
#         A prompt asking about symptom location.
#     """
#     return f"Can you point to where exactly you experience the {symptom}? Which part of your body is affected?"

# @tool
# def get_related_symptoms_tool(symptom: str) -> str:
#     """
#     Ask if there are any other symptoms that might be related to the primary symptom.
    
#     Args:
#         symptom: The name of the symptom to inquire about.
        
#     Returns:
#         A prompt asking about related symptoms.
#     """
#     return f"Are there any other symptoms that you've noticed alongside your {symptom}?"

# @tool
# def get_specialist_recommendation_tool(symptoms: List[str], details: Dict[str, Any]) -> str:
#     """
#     Recommend an appropriate medical specialist based on the reported symptoms and details.
    
#     Args:
#         symptoms: A list of reported symptoms.
#         details: A dictionary containing details about each symptom.
        
#     Returns:
#         A recommendation for which type of medical specialist to consult.
#     """
#     # In a real implementation, this would contain logic to match symptoms to specialists
#     # For demonstration purposes, we'll just return a placeholder
#     return "Based on the symptoms and details provided, I would recommend consulting with a specialist."

def get_symptom_details(symptom: str) -> str:
    return f"Can you describe your {symptom} in more detail?"

def get_symptom_duration(symptom: str) -> str:
    return f"How long have you been experiencing {symptom}? (days, weeks, months?)"

def get_symptom_severity(symptom: str) -> str:
    return f"On a scale of 1-10, how severe is your {symptom}?"

def get_symptom_location(symptom: str) -> str:
    return f"Where exactly do you feel the {symptom}?"

def get_related_symptoms(symptom: str) -> str:
    return f"Are there any other symptoms occurring alongside your {symptom}?"

def get_specialist_recommendation(symptoms: List[str]) -> str:
    return f"Based on {', '.join(symptoms)}, a consultation with a specialist is advised."

# Register tools
get_symptom_details_tool = Tool(
    name="Symptom Details", 
    func=get_symptom_details,
    description="Get detailed information about a specific symptom"
)

get_symptom_duration_tool = Tool(
    name="Symptom Duration", 
    func=get_symptom_duration,
    description="Get information about how long a symptom has been experienced"
)

get_symptom_severity_tool = Tool(
    name="Symptom Severity", 
    func=get_symptom_severity,
    description="Get information about the severity of a symptom on a scale of 1-10"
)

get_symptom_location_tool = Tool(
    name="Symptom Location", 
    func=get_symptom_location,
    description="Get information about where on the body a symptom is experienced"
)

get_related_symptoms_tool = Tool(
    name="Related Symptoms", 
    func=get_related_symptoms,
    description="Get information about other symptoms that might be related"
)

get_specialist_recommendation_tool = Tool(
    name="Specialist Recommendation", 
    func=get_specialist_recommendation,
    description="Get a recommendation for which medical specialist to see based on symptoms"
)
