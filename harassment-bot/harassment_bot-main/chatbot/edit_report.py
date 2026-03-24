from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from config import llm
def edit_the_report(report, user_input, llm):
    

    prompt_template = ChatPromptTemplate.from_template("""
        You are an assistant helping a user edit a report. Below is the current version of the report:
        
        Report:
        
        {report}

        The user wants to make changes. Ask the user for all the changes they want to make, one at a time, and summarize their requests.
        Once the user says 'complete changes,' finalize the changes to the report based on their input and return the updated report.
        If any edits are unclear, ask for clarification before finalizing.

        User Input:
        {user_input}

        Respond in a structured format to handle the conversation and apply changes.
        """
        
    )

    # Initialize the LLM chain
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Variable to hold user changes
    changes_summary = []

    # Simulate conversation loop for collecting edits
    while True:
        # Pass the current user input and report to the LLM
        response = chain.run(report=report, user_input=user_input).strip()

        print("Assistant:", response)

        # Check if the user indicates they're done editing
        if "complete changes" in user_input.lower():
            print("Assistant: Finalizing changes.")
            break

        # Collect user input for additional changes
        user_input = input("User: ")  # Replace with actual input collection in chatbot
        changes_summary.append(user_input)

    # Apply all collected changes to the report
    final_report = apply_changes_to_report(report, changes_summary, llm)

    return final_report

def apply_changes_to_report(report, changes_summary, llm):
    """
    Applies all user-requested changes to the report using the LLM.

    Args:
        report (str): The original report content.
        changes_summary (list): A list of changes requested by the user.
        llm: The LLM instance to help apply changes.

    Returns:
        str: The updated report after applying changes.
    """

    # Define a prompt to apply changes
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an assistant tasked with updating a report based on the following requested changes:

        Original Report:
        
        {report}

        
        Changes Requested:
        {changes_summary}

        Please update the report accordingly and ensure it is coherent and professional. Return the updated report.
        """
    )

    # Run the LLM to generate the updated report
    chain = LLMChain(llm=llm, prompt=prompt_template)
    updated_report = chain.run(report=report, changes_summary="\n".join(changes_summary)).strip()

    return updated_report
