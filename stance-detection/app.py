import streamlit as st
import json
from helper import detect_stance
import time

# Set page configuration
st.set_page_config(
    page_title="Multi-Agent Stance Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
    }
    .subheader {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 500;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #333333;
    }
    .stance-FAVOR, .stance-favor {
        color: #2E7D32;
        font-weight: 600;
    }
    .stance-AGAINST, .stance-against {
        color: #C62828;
        font-weight: 600;
    }
    .stance-NEUTRAL, .stance-neutral {
        color: #0277BD;
        font-weight: 600;
    }
    .confidence-high {
        color: #2E7D32;
        font-weight: 600;
    }
    .confidence-medium {
        color: #FB8C00;
        font-weight: 600;
    }
    .confidence-low {
        color: #D32F2F;
        font-weight: 600;
    }
    .json-viewer {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }
    .agent-card {
        border-left: 4px solid #1E88E5;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f8f9fa; 
        border-radius: 0 8px 8px 0;
        color: #333333;
    }
    .evidence-item {
        background-color: #e3f2fd;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 4px 0;
        display: inline-block;
        font-size: 0.9rem;
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>Multi-Agent Stance Detection</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Collaborative AI analysis of stance in text</p>", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.markdown("### About This System")
    st.markdown("""
    This application analyzes stance in text using a collaborative team of AI agents, each with specialized expertise:
    
    1. **Content Analyzer** - identifies linguistic markers
    2. **Context Researcher** - gathers factual background
    3. **Perspective Agent** - maps diverse viewpoints
    4. **Devil's Advocate** - challenges assumptions
    5. **Synthesis Agent** - determines final stance
    """)
    
    st.markdown("### How It Works")
    st.markdown("""
    The system works by:
    1. Analyzing the text and target topic provided
    2. Analyzing linguistic features and claims
    3. Researching factual context and perspectives
    4. Critically examining arguments and evidence
    5. Synthesizing all inputs to determine stance
    """)
    
    st.markdown("### Stance Classifications")
    st.markdown("""
    - **FAVOR**: Text supports or advocates for the target
    - **AGAINST**: Text opposes or criticizes the target
    - **NEUTRAL**: Text presents a balanced view
    """)
    
    st.markdown("### Output Format")
    st.markdown("""
    Results are structured as:
    ```json
    {
      "final_stance": "<favor/against/neutral>",
      "confidence": <0-1>,
      "supporting_evidence": ["<phrases>"],
      "agent_analyses": {
        "content_analyzer": { ... },
        "context_researcher": { ... },
        "perspective_agent": { ... },
        "devils_advocate": { ... }
      }
    }
    ```
    """)

# Main content area
st.markdown("""
Enter a text passage and specify the target topic for stance detection. 
The system will determine whether the text is in favor of, against, or neutral toward that target.
""")

# Example presets
example_texts = {
    "Climate Change": {
        "text": """Climate change poses an existential threat to our planet. The scientific consensus is clear
        that human activities are the primary driver, and urgent action is needed. We must transition
        to renewable energy, reduce carbon emissions, and implement sustainable policies before it's
        too late. While some may cite economic concerns, the long-term costs of inaction far exceed
        the investments needed today.""",
        "target": "climate change"
    },
    
    "Artificial Intelligence": {
        "text": """Artificial intelligence is transforming our world in unprecedented ways. While AI offers tremendous
        benefits in healthcare, education, and productivity, we must proceed with caution. The potential risks
        of unchecked AI development include job displacement, privacy concerns, and algorithmic bias. A balanced
        approach with thoughtful regulation can help ensure AI benefits humanity while minimizing harms.""",
        "target": "artificial intelligence"
    },
    
    "Social Media": {
        "text": """Social media platforms have become toxic cesspools of misinformation and divisiveness.
        They exploit users' attention through addictive design patterns, harvest personal data, and prioritize
        engagement over truth. These platforms have undermined democratic discourse, enabled foreign interference
        in elections, and contributed to rising anxiety and depression, especially among young people. It's time
        for serious regulation and accountability.""",
        "target": "social media"
    }
}

# Example selector
selected_example = st.selectbox("Try an example:", ["--Select an example--"] + list(example_texts.keys()))

# Create two columns for inputs
col1, col2 = st.columns([3, 1])

# Text input area
with col1:
    if selected_example != "--Select an example--":
        text_input = st.text_area(
            "Text to analyze:", 
            value=example_texts[selected_example]["text"], 
            height=150,
            key="text_input"
        )
    else:
        text_input = st.text_area(
            "Text to analyze:", 
            height=150, 
            placeholder="Enter text to analyze for stance detection...",
            key="text_input"
        )

# Target input area
with col2:
    if selected_example != "--Select an example--":
        target_input = st.text_input(
            "Target topic:", 
            value=example_texts[selected_example]["target"],
            key="target_input"
        )
    else:
        target_input = st.text_input(
            "Target topic:", 
            placeholder="e.g., climate change, abortion, AI",
            key="target_input"
        )
    
    st.markdown("""
    <div style="margin-top: 10px; padding: 10px; background-color: #f0f7ff; border-radius: 5px; border: 1px solid #d0d7de;">
        <small style="color: #333333; font-weight: 500;">Leave blank to auto-detect the target topic from text.</small>
    </div>
    """, unsafe_allow_html=True)

# Analysis button
analyze_button = st.button("Analyze Stance", type="primary", use_container_width=True)

# Process and display results
if analyze_button and text_input:
    # Create an input object
    input_data = {
        "text": text_input,
        "target": target_input
    }
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate the multi-step analysis process
    status_text.text("Preparing analysis...")
    progress_bar.progress(10)
    time.sleep(0.5)
    
    # Display the actual analysis steps
    with st.spinner("Analyzing stance... This may take a minute or two."):
        # Run the actual analysis
        try:
            status_text.text("Analyzing linguistic features...")
            progress_bar.progress(20)
            
            result = detect_stance(input_data)
            
            # Update progress throughout
            status_text.text("Researching factual context...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("Mapping diverse perspectives...")
            progress_bar.progress(70)
            time.sleep(0.5)
            
            status_text.text("Critically examining arguments...")
            progress_bar.progress(90)
            time.sleep(0.5)
            
            status_text.text("Determining final stance...")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # Clear the progress indicators
            status_text.empty()
            
            # Display results
            st.markdown("## Analysis Results")
            
            # Get confidence category
            confidence = result["confidence"]
            if confidence >= 0.7:
                confidence_category = "high"
            elif confidence >= 0.4:
                confidence_category = "medium"
            else:
                confidence_category = "low"
            
            # Format confidence as percentage
            confidence_pct = f"{int(confidence * 100)}%"
            
            # Top summary card
            st.markdown("""
            <div class="info-box">
                <h3>Stance Analysis Summary</h3>
                <table style="width:100%">
                    <tr>
                        <td style="width:25%"><strong>Target:</strong></td>
                        <td>{}</td>
                    </tr>
                    <tr>
                        <td><strong>Stance:</strong></td>
                        <td><span class="stance-{}">{}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Confidence:</strong></td>
                        <td><span class="confidence-{}">{}</span></td>
                    </tr>
                </table>
            </div>
            """.format(
                result["agent_analyses"]["content_analyzer"].get("target", input_data["target"]), 
                result["final_stance"], 
                result["final_stance"],
                confidence_category,
                confidence_pct
            ), unsafe_allow_html=True)
            
            # Supporting evidence
            st.markdown("### Supporting Evidence")
            evidence_html = "<div class='agent-card'>"
            if result["supporting_evidence"]:
                for evidence in result["supporting_evidence"]:
                    evidence_html += f"<div class='evidence-item'>{evidence}</div> "
            else:
                evidence_html += "<p><em>No specific evidence highlights provided.</em></p>"
            evidence_html += "</div>"
            st.markdown(evidence_html, unsafe_allow_html=True)
            
            # Create tabs for agent analyses
            st.markdown("### Agent Analyses")
            tab1, tab2, tab3, tab4 = st.tabs([
                "Content Analysis", 
                "Context Research", 
                "Perspective Mapping", 
                "Critical Examination"
            ])
            
            with tab1:
                content_analysis = result["agent_analyses"]["content_analyzer"]
                st.markdown("#### Linguistic Analysis")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                st.markdown(content_analysis.get("reasoning", "No linguistic analysis available."))
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("#### Key Phrases")
                phrases_html = "<div class='agent-card'>"
                for phrase in content_analysis.get("key_phrases", []):
                    phrases_html += f"<div class='evidence-item'>{phrase}</div> "
                phrases_html += "</div>"
                st.markdown(phrases_html, unsafe_allow_html=True)
                
                st.markdown(f"**Overall Sentiment:** {content_analysis.get('sentiment', 'neutral')}")
            
            with tab2:
                context_research = result["agent_analyses"]["context_researcher"]
                st.markdown("#### Background Information")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                for info in context_research.get("background_info", []):
                    st.markdown(f"• {info}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("#### Common Argument Patterns")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                for pattern in context_research.get("argument_patterns", []):
                    st.markdown(f"• {pattern}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab3:
                perspective_analysis = result["agent_analyses"]["perspective_agent"]
                st.markdown("#### Ideological Perspectives")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                for perspective, interpretation in perspective_analysis.get("ideological_interpretations", {}).items():
                    st.markdown(f"**{perspective}:** {interpretation}")
                    st.markdown("---")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab4:
                devils_analysis = result["agent_analyses"]["devils_advocate"]
                st.markdown("#### Counter Arguments")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                for counter in devils_analysis.get("counter_arguments", []):
                    st.markdown(f"• {counter}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("#### Identified Biases")
                st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
                for bias in devils_analysis.get("identified_biases", []):
                    st.markdown(f"• {bias}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Option to view raw JSON
            with st.expander("View Raw JSON Output"):
                st.json(result)
            
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #fef8f6; border-left: 4px solid #C62828; margin: 20px 0;">
                <h3 style="color: #C62828;">Analysis Error</h3>
                <p>We encountered an error during the analysis. This could be due to:</p>
                <ul>
                    <li>API rate limits or connection issues</li>
                    <li>Text formatting that couldn't be processed</li>
                    <li>Invalid JSON responses from agents</li>
                </ul>
                <p>Please try again with a different text or try again later.</p>
            </div>
            """, unsafe_allow_html=True)

# Add footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Developed using CrewAI multi-agent framework • Structured JSON output format
</div>
""", unsafe_allow_html=True)

# Run this with: streamlit run [app.py](http://_vscodecontentref_/4)