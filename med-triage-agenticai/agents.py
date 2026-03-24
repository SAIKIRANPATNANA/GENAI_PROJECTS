import os
import re
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq

# Initialize global conversation store
SYMPTOM_CONVERSATION = []

# Initialize LLM with Groq
groq_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="gemma2-9b-it",  # Using a stronger model
    temperature=0.2,
    request_timeout=30
)

def receive_symptom_message(message: str, symptoms_list=None):
    """Process a message for symptom analysis using a simple chatbot approach"""
    print(f"Received message: {message}")
    
    try:
        # Add user message to conversation
        user_message = HumanMessage(content=message)
        
        # Don't add duplicate messages
        if not SYMPTOM_CONVERSATION or SYMPTOM_CONVERSATION[-1].content != message:
            SYMPTOM_CONVERSATION.append(user_message)
        
        # Build conversation history for context
        messages_for_llm = []
        
        # Always start with a system prompt
        system_message = """
You are a helpful medical assistant chatbot. Your job is to ask questions about the patient's symptoms 
and provide a recommendation for which specialist they should see.

Guidelines:
1. Ask ONE question at a time about the symptoms
2. Focus on understanding the duration, severity, location, and pattern
3. After collecting sufficient information (3-4 exchanges), recommend an appropriate specialist
4. Be conversational and empathetic
5. Keep responses concise and clear
6. NEVER include your internal thought process or reasoning in responses
7. Never attempt to diagnose specific conditions
8. Always use markdown formatting for your responses

In your final response, give the detailed report of the symptom analysis and tell the patient to click the "Book Appointment" button to schedule with the specialist.
"""
        messages_for_llm.append(SystemMessage(content=system_message))
        
        # Add the conversation history (limited to last 10 messages for context)
        history_length = min(len(SYMPTOM_CONVERSATION), 10)
        for msg in SYMPTOM_CONVERSATION[-history_length:]:
            messages_for_llm.append(msg)
        
        # Call the model
        response = groq_llm.invoke(input=messages_for_llm)
        
        # Add response to conversation history
        ai_message = AIMessage(content=response.content)
        SYMPTOM_CONVERSATION.append(ai_message)
        
        # Extract any symptom details for the UI (simplified)
        symptom_details = extract_symptom_details_simple(SYMPTOM_CONVERSATION)
        
        # Figure out if we should show booking button
        show_booking = should_show_booking(response.content)
        
        # Return a simplified state object
        return {
            "messages": SYMPTOM_CONVERSATION,
            "symptom_details": symptom_details,
            "show_booking": show_booking,
            "conversation_stage": "analysis" if show_booking else "collection"
        }
        
    except Exception as e:
        print(f"ERROR in receive_symptom_message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Add a fallback response
        fallback_msg = """
## Sorry for the Technical Issue

I apologize, but I'm having trouble processing your message. Please try again or consult with a healthcare professional directly.
"""
        fallback_ai_message = AIMessage(content=fallback_msg)
        SYMPTOM_CONVERSATION.append(fallback_ai_message)
        
        return {
            "messages": SYMPTOM_CONVERSATION,
            "symptom_details": {},
            "show_booking": False,
            "conversation_stage": "error"
        }

def should_show_booking(response: str) -> bool:
    """Check if we should show booking button based on response content"""
    booking_indicators = [
        "book appointment",
        "schedule an appointment", 
        "see a doctor",
        "consult with a",
        "specialist",
        "click the button",
        "recommend"
    ]
    
    response_lower = response.lower()
    return any(indicator in response_lower for indicator in booking_indicators)

def extract_symptom_details_simple(conversation: List) -> Dict:
    """Extract basic symptom information from conversation"""
    symptoms = set()
    details = {}
    
    # First identify all symptoms mentioned
    for msg in conversation:
        if isinstance(msg, HumanMessage):
            # Look for initial symptom report
            match = re.search(r"I have the following symptoms: (.*)", msg.content)
            if match:
                for symptom in match.group(1).split(','):
                    symptom = symptom.strip()
                    if symptom:
                        symptoms.add(symptom)
            
            # Look for other symptoms mentioned
            symptom_patterns = [
                r"(headache|pain|ache|discomfort|soreness|tenderness)",
                r"(nausea|vomiting|dizziness|fatigue|fever|cough)",
                r"(rash|swelling|bleeding|discharge|numbness)"
            ]
            
            for pattern in symptom_patterns:
                matches = re.findall(pattern, msg.content, re.IGNORECASE)
                for match in matches:
                    if match:
                        symptoms.add(match.lower())
    
    # Initialize details dictionary
    for symptom in symptoms:
        details[symptom] = {}
    
    # Extract basic details from conversation
    for msg in conversation:
        msg_text = msg.content.lower()
        
        # Look for duration information
        duration_pattern = r"(\d+)\s*(day|days|week|weeks|month|months|year|years)"
        duration_matches = re.findall(duration_pattern, msg_text)
        for match in duration_matches:
            for symptom in symptoms:
                if symptom in msg_text[:100] and "duration" not in details[symptom]:
                    details[symptom]["duration"] = f"{match[0]} {match[1]}"
        
        # Look for severity information
        severity_patterns = [
            r"(\d+)\s*(/|out of)\s*10",
            r"(mild|moderate|severe|extreme)"
        ]
        
        for pattern in severity_patterns:
            severity_matches = re.findall(pattern, msg_text)
            for match in severity_matches:
                for symptom in symptoms:
                    if "severity" not in details[symptom]:
                        if isinstance(match, tuple):
                            details[symptom]["severity"] = f"{match[0]}/10"
                        else:
                            details[symptom]["severity"] = match
        
        # Look for location information
        for symptom in symptoms:
            location_patterns = [
                fr"(in|on|at|near) (the|my) ([a-z\s]+) {symptom}",
                fr"{symptom} (in|on|at|near) (the|my) ([a-z\s]+)"
            ]
            
            for pattern in location_patterns:
                location_matches = re.findall(pattern, msg_text)
                if location_matches and "location" not in details[symptom]:
                    location = location_matches[0][-1] if isinstance(location_matches[0], tuple) else location_matches[0]
                    details[symptom]["location"] = location
    
    return details