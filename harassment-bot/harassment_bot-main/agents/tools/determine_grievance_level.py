from langchain.tools import tool
from langchain import LLMChain, PromptTemplate

def get_determine_grievance_level(llm):
    @tool("Determine_Grievance_Level")
    def determine_grievance_level(context: str) -> str:
        """Determine the level of the grievance based on the provided context and guide the sequence of actions."""
        prompt_template = PromptTemplate.from_template("""
        Based on the provided context, determine the level of the harassment incident and specify the subsequent actions.
        Context: {context}
        Levels:
        Level 1:
        - Minor incidents that can be addressed informally or through low-level mediation.
        - Examples: Verbal abuse such as demeaning language or public humiliation, minor cyber harassment like excessive messaging.
        - Response time: Within a week.

        Level 2:
        - Incidents requiring prompt attention due to moderate impact or escalation risk.
        - Examples: Bullying, cyber harassment involving inappropriate content or account hacking, or initial signs of stalking like unsolicited gifts.
        - Response time: Within 3 to 7 days.

        Level 3:
        - Serious incidents requiring immediate attention due to physical or emotional harm.
        - Examples: Sexual harassment involving coercive requests or unwelcome touching, stalking involving monitoring movements, or discrimination causing significant exclusion.
        - Response time: Immediate resolution.

        Level 4:
        - Severe incidents involving violence, threats, or abuse of authority.
        - Examples: Sexual harassment with physical violence, stalking with malicious intent, abuse of authority involving physical threats, or discrimination coupled with violence.
        - Response time: Urgent resolution, escalation to top-level authorities.
        """)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        level = chain.run(context=context)
        return level
    
    return determine_grievance_level