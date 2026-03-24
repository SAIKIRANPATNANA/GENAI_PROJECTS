# from typing import List, Dict, Any
# from langchain_core.messages import HumanMessage, AIMessage

# class SymptomAnalysisTask:
#     """Task for analyzing symptoms and providing initial triage recommendations"""
    
#     def __init__(self, symptoms: List[str]):
#         self.symptoms = symptoms
#         self.collected_details = {symptom: {} for symptom in symptoms}
        
#     def get_collection_instruction(self) -> str:
#         """Get the instruction for symptom collection phase"""
#         return f"""
#         You are a compassionate medical triage assistant.
#         The patient has reported these symptoms: {', '.join(self.symptoms)}
        
#         Your task is to gather all necessary details about each symptom:
#         1. Duration (how long they've experienced each symptom)
#         2. Severity (on a scale of 1-10)
#         3. Location/region of the body
#         4. Pattern (constant, intermittent, getting worse, etc.)
#         5. Any triggers or alleviating factors
#         6. Related symptoms they might be experiencing
        
#         Be thorough but conversational. Don't ask about all symptoms at once - focus on one symptom at a time.
#         """
        
#     def get_analysis_instruction(self) -> str:
#         """Get the instruction for analysis phase with collected details"""
#         # Format the collected details for display
#         formatted_details = []
#         for symptom, details in self.collected_details.items():
#             symptom_info = f"- {symptom.upper()}:\n"
#             for key, value in details.items():
#                 symptom_info += f"  • {key.capitalize()}: {value}\n"
#             formatted_details.append(symptom_info)
            
#         details_text = "\n".join(formatted_details)
        
#         return f"""
#         You are a medical triage assistant providing analysis based on reported symptoms.
        
#         SYMPTOM INFORMATION:
#         {details_text}
        
#         Your task:
#         1. Summarize the patient's condition based on reported symptoms
#         2. Recommend which type of medical specialist would be most appropriate
#         3. Provide a brief explanation of your reasoning
#         4. Suggest the patient clicks the "Book Appointment" button to schedule with the recommended specialist
        
#         Important: Do not attempt to diagnose the patient's condition. Focus only on recommending the appropriate specialist.
#         """
        
#     def is_collection_complete(self) -> bool:
#         """Check if we have collected sufficient details for all symptoms"""
#         required_details = ["duration", "severity", "location", "pattern"]
        
#         for symptom in self.symptoms:
#             for detail in required_details:
#                 if detail not in self.collected_details.get(symptom, {}):
#                     return False
#         return True
        
#     def update_collected_details(self, details: Dict[str, Dict[str, Any]]):
#         """Update the collected details with new information"""
#         self.collected_details.update(details)

# class ReportGenerationTask:
#     """Task for generating a detailed medical report based on symptom analysis"""
    
#     def __init__(self, symptom_details: Dict[str, Dict[str, Any]], recommendations: Dict[str, Any]):
#         self.symptom_details = symptom_details
#         self.recommendations = recommendations
        
#     def get_report_instruction(self) -> str:
#         """Get the instruction for report generation"""
#         # Format the symptom details
#         formatted_details = []
#         for symptom, details in self.symptom_details.items():
#             symptom_info = f"- {symptom.upper()}:\n"
#             for key, value in details.items():
#                 symptom_info += f"  • {key.capitalize()}: {value}\n"
#             formatted_details.append(symptom_info)
            
#         details_text = "\n".join(formatted_details)
        
#         specialist = self.recommendations.get("specialist", "appropriate medical specialist")
#         reasoning = self.recommendations.get("reasoning", "")
        
#         return f"""
#         You are a medical report generator.
        
#         SYMPTOM INFORMATION:
#         {details_text}
        
#         SPECIALIST RECOMMENDATION:
#         {specialist}
        
#         REASONING:
#         {reasoning}
        
#         Generate a clear, structured medical triage report that includes:
#         1. Patient symptom summary
#         2. Detailed breakdown of each reported symptom and associated details
#         3. Recommended specialist for consultation
#         4. Reasoning for the specialist recommendation
#         5. A call to action to book an appointment
        
#         Format the report professionally but make it easy to understand for the patient.
#         """

from typing import List, Dict

class SymptomAnalysisTask:
    """Handles symptom collection and structuring"""
    
    def __init__(self, symptoms: List[str]):
        self.symptoms = symptoms
        self.collected_details = {symptom: {} for symptom in symptoms}
        
    def is_complete(self) -> bool:
        """Check if all details are collected"""
        return all(
            all(detail in self.collected_details[symptom] for detail in ["duration", "severity", "location", "pattern"])
            for symptom in self.symptoms
        )

    def update_details(self, details: Dict[str, Dict[str, str]]):
        """Update collected details"""
        self.collected_details.update(details)

class ReportGenerationTask:
    """Handles medical report formatting"""
    
    def __init__(self, symptom_details: Dict[str, Dict[str, str]], specialist: str):
        self.symptom_details = symptom_details
        self.specialist = specialist
        
    def generate_report(self) -> str:
        """Generate structured medical report"""
        formatted_details = "\n".join(
            f"- {symptom.upper()}:\n" +
            "\n".join(f"  • {key.capitalize()}: {value}" for key, value in details.items())
            for symptom, details in self.symptom_details.items()
        )
        
        # 🔹 **Add the prompt here**
        report_prompt = f"""
        # **Medical Symptom Analysis Report**  
        
        ### **Patient's Reported Symptoms:**  
        {formatted_details}  
        
        ### **Recommended Specialist:**  
        🩺 {self.specialist}  
        
        ⚠️ *This is a preliminary triage suggestion. Please consult a medical professional for an official diagnosis.*  
        
        **Would you like to book an appointment now?** [Click Here]  
        """
        
        return report_prompt
