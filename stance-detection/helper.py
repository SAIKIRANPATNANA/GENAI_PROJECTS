# import os
# from typing import Dict

# # Import CrewAI components
# from crewai import Agent, Task, Crew
# from crewai.process import Process
# from langchain_groq import ChatGroq
# from crewai_tools import SerperDevTool

# # Set API keys through environment variables
# # os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
# # os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "")

# # Initialize tools
# search_tool = SerperDevTool()

# # Initialize LLM
# llm = ChatGroq(
#     temperature=0.1,
#     model_name="llama3-70b-8192",
#     api_key=os.environ["GROQ_API_KEY"]
# )

# # Define the agents
# content_analyzer = Agent(
#     llm=llm,
#     role="Content Analyzer",
#     goal="Extract key claims and evidence from text to determine linguistic markers of stance",
#     backstory="You specialize in linguistic analysis to identify explicit and implicit stance indicators. "
#              "You can recognize rhetorical devices, emotive language, modal expressions, and other "
#              "textual features that signal an author's position on a topic. Your expertise allows you to "
#              "break down complex texts and extract the main claims, arguments, and evidence.",
#     verbose=True,
#     allow_delegation=False  # Prevent delegation
# )

# context_researcher = Agent(
#     llm=llm,
#     role="Context Researcher",
#     goal="Research factual background information to establish objective context for stance analysis",
#     backstory="You are an expert researcher who gathers factual, historical, and scientific context "
#               "about topics. You provide objective information from reliable sources to establish "
#               "the factual landscape surrounding the stance target. You focus on verifiable information "
#               "rather than opinions or interpretations.",
#     tools=[search_tool],
#     verbose=True,
#     allow_delegation=False  # Prevent delegation
# )

# perspective_agent = Agent(
#     llm=llm,
#     role="Perspective Agent",
#     goal="Consider multiple viewpoints across ideological, cultural, and stakeholder dimensions",
#     backstory="You specialize in mapping the landscape of perspectives on contentious issues. "
#               "You identify how different stakeholders, ideological groups, and cultural perspectives "
#               "approach the topic. Your strength is in providing charitable interpretations of "
#               "diverse viewpoints to ensure all relevant perspectives are considered.",
#     verbose=True,
#     allow_delegation=False  # Prevent delegation
# )

# devils_advocate = Agent(
#     llm=llm,
#     role="Devil's Advocate",
#     goal="Challenge assumptions, identify biases, and test the strength of arguments through critical analysis",
#     backstory="You excel at identifying logical fallacies, questionable evidence, implicit biases, "
#               "and weaknesses in argumentation. Your role is to challenge the strongest arguments "
#               "and ensure a rigorous examination of all claims. You help avoid confirmation bias by "
#               "questioning what might otherwise be taken for granted.",
#     verbose=True,
#     allow_delegation=False  # Prevent delegation
# )

# synthesis_agent = Agent(
#     llm=llm,
#     role="Synthesis Agent",
#     goal="Determine final stance by integrating analyses and weighing competing considerations",
#     backstory="You are skilled at weighing evidence, balancing competing perspectives, and "
#               "reaching nuanced conclusions about stance. You can integrate linguistic analysis, "
#               "factual context, multiple perspectives, and critical challenges into a coherent "
#               "determination of stance with appropriate confidence levels.",
#     verbose=True,
#     allow_delegation=False  # Prevent delegation
# )

# def detect_stance(text: str) -> Dict:
#     """
#     Run the stance detection crew on the provided text
    
#     Args:
#         text: The text to analyze for stance
        
#     Returns:
#         Dictionary containing the analysis results
#     """
#     print(f"\nAnalyzing text for stance detection: {text[:100]}...")
    
#     # Identify stance target
#     target_prompt = f"Extract the specific target (topic, entity, or issue) for stance detection from this text: {text}. Respond ONLY with the name of the target."
#     target_response = llm.invoke(target_prompt)
#     stance_target = target_response.content.strip()
    
#     print(f"Identified stance target: {stance_target}")
    
#     # Define the tasks with actual text and target directly in the descriptions
#     # Content Analysis Task
#     analyze_content_task = Task(
#         description=(
#             f"Analyze the linguistic features of this specific text to identify stance markers:\n\n"
#             f"\"{text}\"\n\n"
#             f"The target is: {stance_target}\n\n"
#             "Your analysis should:\n"
#             "1. Identify explicit stance markers (direct statements of position, evaluative language)\n"
#             "2. Recognize implicit stance indicators (presuppositions, framing, rhetorical questions)\n"
#             "3. Extract the main claims and arguments being presented\n"
#             "4. Note any evidence cited to support the claims\n"
#             "5. Analyze rhetorical strategies that signal stance\n\n"
#             "Format your response as a structured analysis with sections for explicit markers, "
#             "implicit markers, key claims, supporting evidence, and rhetorical strategies.\n\n"
#             "Begin with 'CONTENT ANALYSIS:' and end with '---END CONTENT ANALYSIS---'."
#         ),
#         agent=content_analyzer,
#         expected_output="A detailed linguistic analysis of stance markers in the text"
#     )
    
#     # Research Context Task
#     research_context_task = Task(
#         description=(
#             f"Research factual background information on {stance_target} to provide objective context.\n\n"
#             f"Research this topic: {stance_target}\n\n"
#             f"This is the original text:\n\"{text}\"\n\n"
#             "Your research should:\n"
#             "1. Gather factual, historical, and scientific information about the target topic\n"
#             "2. Find objective data and statistics relevant to evaluating the claims\n"
#             "3. Identify the current factual consensus on key aspects of the topic\n"
#             "4. Note areas of factual uncertainty or ongoing research\n"
#             "5. Provide information from diverse reliable sources\n\n"
#             "Ensure your research is factual rather than opinion-based, and provide proper attribution for key information.\n\n"
#             "Begin with 'BACKGROUND INFORMATION:' and end with '---END BACKGROUND---'."
#         ),
#         agent=context_researcher,
#         expected_output="An objective factual background briefing on the topic"
#     )
    
#     # Perspective Analysis Task
#     analyze_perspectives_task = Task(
#         description=(
#             f"Map the landscape of perspectives on {stance_target} across different dimensions.\n\n"
#             f"Original text:\n\"{text}\"\n\n"
#             f"Target: {stance_target}\n\n"
#             "Your analysis should:\n"
#             "1. Identify major ideological perspectives on this issue (conservative, liberal, libertarian, etc.)\n"
#             "2. Map perspectives of key stakeholder groups affected by or concerned with the issue\n"
#             "3. Note cultural, religious, or philosophical frameworks that inform different positions\n"
#             "4. Present each perspective charitably, articulating its strongest form\n"
#             "5. Highlight areas of consensus and disagreement across perspectives\n\n"
#             "Ensure balanced coverage of the full spectrum of perspectives, beyond simple pro/con dichotomies.\n\n"
#             "Begin with 'PERSPECTIVE ANALYSIS:' and end with '---END PERSPECTIVES---'."
#         ),
#         agent=perspective_agent,
#         expected_output="A comprehensive mapping of perspectives on the topic"
#     )
    
#     # Critique Arguments Task
#     critique_arguments_task = Task(
#         description=(
#             f"Critically examine the claims, evidence, and perspectives on {stance_target}.\n\n"
#             f"Original text:\n\"{text}\"\n\n"
#             f"Target: {stance_target}\n\n"
#             "Your critical examination should:\n"
#             "1. Identify potential biases in the original text's framing and language\n"
#             "2. Test the logical structure of the main arguments for fallacies\n"
#             "3. Evaluate the quality and relevance of evidence presented\n"
#             "4. Highlight important counterarguments not addressed\n"
#             "5. Note assumptions that may be questionable\n\n"
#             "Focus particularly on the strongest arguments in the text and subject them to rigorous scrutiny.\n\n"
#             "Begin with 'CRITICAL ANALYSIS:' and end with '---END CRITIQUE---'."
#         ),
#         agent=devils_advocate,
#         expected_output="A critical evaluation of the arguments, evidence, and potential biases"
#     )
    
#     # Stance Determination Task
#     determine_stance_task = Task(
#         description=(
#             f"Determine the final stance expressed in this text toward {stance_target}:\n\n"
#             f"\"{text}\"\n\n"
#             "Your stance determination should:\n"
#             "1. Classify the stance as FAVOR (supporting/advocating), AGAINST (opposing/criticizing), "
#             "NEUTRAL (balanced/objective), or NONE (no stance expressed)\n"
#             "2. Assign a confidence level (LOW, MEDIUM, HIGH) to your determination\n"
#             "3. Provide a nuanced explanation justifying your conclusion\n"
#             "4. Note any ambiguities or complexities that made stance detection challenging\n"
#             "5. Explain how the various analyses contributed to your final determination\n\n"
#             "Remember that stance may be expressed through implications, framing, and selective emphasis, "
#             "not just explicit statements.\n\n"
#             "Begin with 'FINAL STANCE DETERMINATION:' and end with '---END DETERMINATION---'."
#         ),
#         agent=synthesis_agent,
#         expected_output="A final stance determination with confidence level and detailed justification"
#     )
    
#     # Create the crew with these specific tasks
#     stance_detection_crew = Crew(
#         agents=[content_analyzer, context_researcher, perspective_agent, devils_advocate, synthesis_agent],
#         tasks=[analyze_content_task, research_context_task, analyze_perspectives_task, critique_arguments_task, determine_stance_task],
#         verbose=2,
#         process=Process.sequential,  # Ensure tasks run in sequence
#         allow_delegation=False  # Prevent delegation at crew level
#     )
    
#     # Run the crew with the text and target
#     result = stance_detection_crew.kickoff()
    
#     # Process the results
#     structured_result = process_agent_output(result, stance_target)
    
#     return structured_result

# def process_agent_output(result: str, stance_target: str) -> Dict:
#     """
#     Process the raw output from the crew into a structured format
#     """
#     print("\nProcessing agent output...")
    
#     # Initialize structure
#     sections = {
#         "stance_target": stance_target,
#         "final_stance": "No final stance determined",
#         "stance_classification": "UNKNOWN",
#         "confidence_level": "UNKNOWN"
#     }
    
#     if "FINAL STANCE DETERMINATION:" in result and "---END DETERMINATION---" in result:
#         sections["final_stance"] = result.split("FINAL STANCE DETERMINATION:")[1].split("---END DETERMINATION---")[0].strip()
#         print("✓ Extracted final stance determination")
    
#     # Extract stance classification and confidence from final stance
#     final_stance = sections["final_stance"].upper()
    
#     if "FAVOR" in final_stance:
#         sections["stance_classification"] = "FAVOR"
#     elif "AGAINST" in final_stance:
#         sections["stance_classification"] = "AGAINST"
#     elif "NEUTRAL" in final_stance:
#         sections["stance_classification"] = "NEUTRAL"
#     elif "NONE" in final_stance:
#         sections["stance_classification"] = "NONE"
    
#     if "HIGH CONFIDENCE" in final_stance or "CONFIDENCE: HIGH" in final_stance or 'HIGH' in final_stance:
#         sections["confidence_level"] = "HIGH"
#     elif "MEDIUM CONFIDENCE" in final_stance or "CONFIDENCE: MEDIUM" in final_stance or 'MEDIUM' in final_stance:
#         sections["confidence_level"] = "MEDIUM"
#     elif "LOW CONFIDENCE" in final_stance or "CONFIDENCE: LOW" in final_stance or 'LOW' in final_stance:
#         sections["confidence_level"] = "LOW"
    
#     print(f"Stance classification: {sections['stance_classification']}")
#     print(f"Confidence level: {sections['confidence_level']}")
    
#     return sections

# # Example usage
# if __name__ == "__main__":
#     sample_text = """
#    Abortion is the right of the woman
#     """
    
#     result = detect_stance(sample_text)
    
#     print(f"\n=== FINAL RESULTS ===")
#     print(f"Stance Target: {result['stance_target']}")
#     print(f"Stance Classification: {result['stance_classification']}")
#     print(f"Confidence Level: {result['confidence_level']}")
#     print(f"Final Stance: {result['final_stance'][:150]}...")
import os
import json
from typing import Dict, List, Any
import re

# Import CrewAI components
from crewai import Agent, Task, Crew
from crewai.process import Process
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool

# Set API keys from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

if not groq_api_key or not serper_api_key:
    raise ValueError("GROQ_API_KEY and SERPER_API_KEY must be set")

os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["SERPER_API_KEY"] = serper_api_key

# Initialize tools
search_tool = SerperDevTool()

# Initialize LLM
llm = ChatGroq(
    temperature=0.1,
    model_name="llama3-70b-8192",
    api_key=os.environ["GROQ_API_KEY"]
)

# Define the agents
content_analyzer = Agent(
    llm=llm,
    role="Content Analyzer",
    goal="Extract key claims and evidence from text to determine linguistic markers of stance",
    backstory="You specialize in linguistic analysis to identify explicit and implicit stance indicators. "
             "You can recognize rhetorical devices, emotive language, modal expressions, and other "
             "textual features that signal an author's position on a topic. Your expertise allows you to "
             "break down complex texts and extract the main claims, arguments, and evidence.",
    verbose=True,
    allow_delegation=False
)

context_researcher = Agent(
    llm=llm,
    role="Context Researcher",
    goal="Research factual background information to establish objective context for stance analysis",
    backstory="You are an expert researcher who gathers factual, historical, and scientific context "
              "about topics. You provide objective information from reliable sources to establish "
              "the factual landscape surrounding the stance target. You focus on verifiable information "
              "rather than opinions or interpretations.",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False
)

perspective_agent = Agent(
    llm=llm,
    role="Perspective Agent",
    goal="Consider multiple viewpoints across ideological, cultural, and stakeholder dimensions",
    backstory="You specialize in mapping the landscape of perspectives on contentious issues. "
              "You identify how different stakeholders, ideological groups, and cultural perspectives "
              "approach the topic. Your strength is in providing charitable interpretations of "
              "diverse viewpoints to ensure all relevant perspectives are considered.",
    verbose=True,
    allow_delegation=False
)

devils_advocate = Agent(
    llm=llm,
    role="Devil's Advocate",
    goal="Challenge assumptions, identify biases, and test the strength of arguments through critical analysis",
    backstory="You excel at identifying logical fallacies, questionable evidence, implicit biases, "
              "and weaknesses in argumentation. Your role is to challenge the strongest arguments "
              "and ensure a rigorous examination of all claims. You help avoid confirmation bias by "
              "questioning what might otherwise be taken for granted.",
    verbose=True,
    allow_delegation=False
)

synthesis_agent = Agent(
    llm=llm,
    role="Synthesis Agent",
    goal="Determine final stance by integrating analyses and weighing competing considerations",
    backstory="You are skilled at weighing evidence, balancing competing perspectives, and "
              "reaching nuanced conclusions about stance. You can integrate linguistic analysis, "
              "factual context, multiple perspectives, and critical challenges into a coherent "
              "determination of stance with appropriate confidence levels.",
    verbose=True,
    allow_delegation=False
)

def detect_stance(input_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Run the stance detection crew on the provided text and target
    
    Args:
        input_data: Dictionary containing the text and target to analyze
            {
              "text": "<input_text>",  
              "target": "<topic_or_claim>"
            }
        
    Returns:
        Dictionary containing the analysis results in the specified format
    """
    text = input_data.get("text", "")
    target = input_data.get("target", "")
    
    print(f"\nAnalyzing text for stance detection: {text[:100]}...")
    print(f"Target: {target}")
    
    # If target is not provided, extract it from text
    if not target:
        target_prompt = f"Extract the specific target (topic, entity, or issue) for stance detection from this text: {text}. Respond ONLY with the name of the target."
        target_response = llm.invoke(target_prompt)
        target = target_response.content.strip()
        print(f"Extracted stance target: {target}")
    
    # Content Analysis Task - updated to produce structured output
    analyze_content_task = Task(
        description=(
            f"Analyze the linguistic features of this specific text to identify stance markers:\n\n"
            f"\"{text}\"\n\n"
            f"The target is: {target}\n\n"
            "Your analysis should:\n"
            "1. Identify explicit stance markers (direct statements of position, evaluative language)\n"
            "2. Recognize implicit stance indicators (presuppositions, framing, rhetorical questions)\n"
            "3. Extract the main claims and arguments being presented\n"
            "4. Note any evidence cited to support the claims\n"
            "5. Analyze rhetorical strategies that signal stance\n\n"
            "6. Extract a list of key phrases that indicate stance\n"
            "7. Determine the overall sentiment (positive/negative/neutral)\n\n"
            "Format your response in this exact JSON structure:\n\n"
            "```json\n"
            "{\n"
            '  "reasoning": "<your detailed linguistic analysis>",\n'
            '  "key_phrases": ["<key phrase 1>", "<key phrase 2>", "..."],\n'
            '  "sentiment": "<positive/negative/neutral>"\n'
            "}\n"
            "```\n\n"
            "Ensure your response is valid JSON."
        ),
        agent=content_analyzer,
        expected_output="A detailed linguistic analysis in JSON format"
    )
    
    # Research Context Task - updated to produce structured output
    research_context_task = Task(
        description=(
            f"Research factual background information on {target} to provide objective context.\n\n"
            f"Research this topic: {target}\n\n"
            f"This is the original text:\n\"{text}\"\n\n"
            "Your research should:\n"
            "1. Gather factual, historical, and scientific information about the target topic\n"
            "2. Find objective data and statistics relevant to evaluating the claims\n"
            "3. Identify common argument patterns in discourse about this topic\n"
            "4. Note areas of factual uncertainty or ongoing research\n\n"
            "Format your response in this exact JSON structure:\n\n"
            "```json\n"
            "{\n"
            '  "background_info": ["<relevant fact 1>", "<relevant fact 2>", "..."],\n'
            '  "argument_patterns": ["<common discourse pattern 1>", "<common discourse pattern 2>", "..."]\n'
            "}\n"
            "```\n\n"
            "Ensure your response is valid JSON."
        ),
        agent=context_researcher,
        expected_output="Factual background information in JSON format"
    )
    
    # Perspective Analysis Task - updated to produce structured output
    analyze_perspectives_task = Task(
        description=(
            f"Map the landscape of perspectives on {target} across different dimensions.\n\n"
            f"Original text:\n\"{text}\"\n\n"
            f"Target: {target}\n\n"
            "Your analysis should:\n"
            "1. Identify major ideological perspectives on this issue (conservative, liberal, libertarian, etc.)\n"
            "2. For each perspective, provide a charitable interpretation of how they would view this topic\n"
            "3. Note cultural, religious, or philosophical frameworks that inform different positions\n\n"
            "Format your response in this exact JSON structure:\n\n"
            "```json\n"
            "{\n"
            '  "ideological_interpretations": {\n'
            '    "<perspective 1>": "<interpretation 1>",\n'
            '    "<perspective 2>": "<interpretation 2>",\n'
            '    "...": "..."\n'
            "  }\n"
            "}\n"
            "```\n\n"
            "Ensure your response is valid JSON."
        ),
        agent=perspective_agent,
        expected_output="A mapping of perspectives in JSON format"
    )
    
    # Critique Arguments Task - updated to produce structured output
    critique_arguments_task = Task(
        description=(
            f"Critically examine the claims, evidence, and perspectives on {target}.\n\n"
            f"Original text:\n\"{text}\"\n\n"
            f"Target: {target}\n\n"
            "Your critical examination should:\n"
            "1. Identify potential biases in the original text's framing and language\n"
            "2. Develop counterarguments to the main claims\n"
            "3. Provide alternative readings of the evidence presented\n"
            "4. Highlight assumptions that may be questionable\n\n"
            "Format your response in this exact JSON structure:\n\n"
            "```json\n"
            "{\n"
            '  "counter_arguments": ["<alternative reading 1>", "<alternative reading 2>", "..."],\n'
            '  "identified_biases": ["<potential bias 1>", "<potential bias 2>", "..."]\n'
            "}\n"
            "```\n\n"
            "Ensure your response is valid JSON."
        ),
        agent=devils_advocate,
        expected_output="Critical analysis in JSON format"
    )
    
    # Stance Determination Task - updated to produce structured output
    determine_stance_task = Task(
        description=(
            f"Determine the final stance expressed in this text toward {target}:\n\n"
            f"\"{text}\"\n\n"
            "Your stance determination should:\n"
            "1. Classify the stance as FAVOR (supporting/advocating), AGAINST (opposing/criticizing), or NEUTRAL (balanced/objective)\n"
            "2. Assign a confidence level as a decimal between 0 and 1 (e.g., 0.7 for 70% confidence)\n"
            "3. Extract key supporting evidence from the text that justifies your determination\n"
            "4. Consider all analyses from previous agents\n\n"
            "Format your response in this exact JSON structure:\n\n"
            "```json\n"
            "{\n"
            '  "final_stance": "<FAVOR/AGAINST/NEUTRAL>",\n'
            '  "confidence": <0-1 decimal>,\n'
            '  "supporting_evidence": ["<key phrase 1>", "<key phrase 2>", "..."]\n'
            "}\n"
            "```\n\n"
            "Ensure your response is valid JSON."
        ),
        agent=synthesis_agent,
        expected_output="Final stance determination in JSON format"
    )
    
    # Create the crew with these specific tasks
    stance_detection_crew = Crew(
        agents=[content_analyzer, context_researcher, perspective_agent, devils_advocate, synthesis_agent],
        tasks=[analyze_content_task, research_context_task, analyze_perspectives_task, critique_arguments_task, determine_stance_task],
        verbose=2,
        process=Process.sequential,  # Ensure tasks run in sequence
        allow_delegation=False  # Prevent delegation at crew level
    )
    
    # Run the crew
    result = stance_detection_crew.kickoff()
    
    # Process the results into the required format
    structured_result = process_agent_output(result, target)
    
    return structured_result

def process_agent_output(result: str, target: str) -> Dict[str, Any]:
    """
    Process the raw output from the crew into the required structured format
    """
    print("\nProcessing agent output...")
    
    # Initialize the output structure
    output = {
        "final_stance": "NEUTRAL",
        "confidence": 0.5,
        "supporting_evidence": [],
        "agent_analyses": {
            "content_analyzer": {
                "reasoning": "",
                "key_phrases": [],
                "sentiment": "neutral"
            },
            "context_researcher": {
                "background_info": [],
                "argument_patterns": []
            },
            "perspective_agent": {
                "ideological_interpretations": {}
            },
            "devils_advocate": {
                "counter_arguments": [],
                "identified_biases": []
            }
        }
    }
    
    # Define regex patterns to extract JSON from the result
    json_pattern = r"```(?:json)?\n([\s\S]*?)```"
    
    # Extract and parse JSON from each agent's output
    json_matches = re.findall(json_pattern, result)
    
    # Process each JSON block based on its content
    for i, json_str in enumerate(json_matches):
        try:
            data = json.loads(json_str.strip())
            
            # Content analyzer output (first task)
            if i == 0 and "reasoning" in data and "key_phrases" in data and "sentiment" in data:
                output["agent_analyses"]["content_analyzer"] = data
                # Also use key phrases as supporting evidence
                output["supporting_evidence"].extend(data.get("key_phrases", []))
            
            # Context researcher output (second task)
            elif i == 1 and "background_info" in data and "argument_patterns" in data:
                output["agent_analyses"]["context_researcher"] = data
            
            # Perspective agent output (third task)
            elif i == 2 and "ideological_interpretations" in data:
                output["agent_analyses"]["perspective_agent"] = data
            
            # Devil's advocate output (fourth task)
            elif i == 3 and "counter_arguments" in data and "identified_biases" in data:
                output["agent_analyses"]["devils_advocate"] = data
            
            # Synthesis agent output (final task)
            elif i == 4 and "final_stance" in data and "confidence" in data and "supporting_evidence" in data:
                output["final_stance"] = data.get("final_stance", "NEUTRAL")
                output["confidence"] = data.get("confidence", 0.5)
                # Combine with any existing evidence
                output["supporting_evidence"] = list(set(output["supporting_evidence"] + data.get("supporting_evidence", [])))
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from agent output {i}: {e}")
            print(f"Problematic JSON string: {json_str[:100]}...")
    
    # If no valid JSON was found for the final stance, try to extract it from text
    if output["final_stance"] == "NEUTRAL" and output["confidence"] == 0.5:
        if "FAVOR" in result.upper():
            output["final_stance"] = "FAVOR"
        elif "AGAINST" in result.upper():
            output["final_stance"] = "AGAINST"
        
        # Try to extract confidence as well
        confidence_pattern = r"confidence:?\s*(0\.\d+|\d+%)"
        confidence_match = re.search(confidence_pattern, result, re.IGNORECASE)
        if confidence_match:
            confidence_str = confidence_match.group(1)
            if "%" in confidence_str:
                # Convert percentage to decimal
                output["confidence"] = float(confidence_str.strip("%")) / 100
            else:
                output["confidence"] = float(confidence_str)
    
    print(f"Final stance: {output['final_stance']}")
    print(f"Confidence: {output['confidence']}")
    print(f"Found {len(output['supporting_evidence'])} pieces of supporting evidence")
    
    return output

# Example usage
if __name__ == "__main__":
    sample_input = {
        "text": "Climate change poses an existential threat to our planet. The scientific consensus is clear that human activities are the primary driver, and urgent action is needed.",
        "target": "climate change"
    }
    
    result = detect_stance(sample_input)
    print("\n=== FINAL RESULTS ===")
    print(json.dumps(result, indent=2))
