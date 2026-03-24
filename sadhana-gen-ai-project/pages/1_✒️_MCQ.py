import streamlit as st
from integrator import *
import time
import random

css = """
<style>
.rainbow-title-text{
    background: -webkit-linear-gradient(45deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
    font-size: 50px; 
    text-align: center;
    animation: rainbow-text-animation 15s ease infinite;
}
@keyframes rainbow-text-animation {
    0% {
        background-position: 0% 50%;
    }
    100% {
        background-position: 100% 50%;
    }
}
</style>
"""

st.markdown(
    """
    <style>
    .stPageLink {
        border: 1px solid #FFFFF0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stPageLink {
        border: 1px solid #FFFFF0;
        padding: 2px 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://webdesigndev.com/wp-content/uploads/2018/04/6a-Texture-Free-Dark-Backgrounds.jpg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()
st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">Multiple Choice Questions</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#F11FEE;'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)


if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file == None:
    if 'uploaded_file' not in st.session_state :
        st.session_state['uploaded_file'] = None
    st.warning('Kindly upload your content pdf on the Home page..!', icon="⚠️")
    st.page_link("✍️_HOME.py", label=":rainbow[Click Me  to go to HOME..!]", icon="✍️")

if 'topic_name' not in st.session_state and 'difficulty_level' not in st.session_state:
    st.session_state['topic_name'] = None 
    st.session_state['difficulty_level'] = None

if 'random' not in st.session_state:
    st.session_state['random'] = -1

if st.session_state.uploaded_file is not None:

    if st.session_state.mode is not None:
        st.session_state.mode = 'objective'
    choice = st.radio("Choose a context", [":rainbow[Overall]",":rainbow[Specific]"], captions = ["Questions would come from entire uploaded content","Questions would come from topic of your choice."])
    if choice == ":rainbow[Overall]" :
        st.session_state.topic_name = 'overall'
    else:
        st.session_state.topic_name = st.text_input('Enter any specific topic name or keyword present in your uploaded content?',placeholder= 'What is Project Sadhana?')
    st.session_state.difficulty_level  = st.selectbox("Select the difficulty level of questions?",("Easy", "Moderate", "Tough"),placeholder="Select difficult level ...")
    if st.session_state.difficulty_level   == 'Easy':
        st.session_state.difficulty_level = 'easy'
    elif st.session_state.difficulty_level == 'Moderate':
        st.session_state.difficulty_level = 'moderate'
    else: 
        st.session_state.difficulty_level = 'tough'
    choice = st.radio("Are you ready for the quiz..?", [":rainbow[No]",":rainbow[Yes]"], captions = ["Set your preferences to be ready for quiz.","Check your preferences before getting started with the quiz."])
    
    if choice == ":rainbow[Yes]":
        with st.expander("Scheme of Evaluation"):
            st.write('- You will be asked 10 multiple choice questions.')
            st.write('- Each question carries one ⭐')
        st.info(':rainbow[All The Very Best] 👍')
        random_number = random.randint(1,1000)
        while(random_number==st.session_state.random):
            random_number = random.randint(1,1000)
        st.session_state.random = random_number
        st.page_link('pages/3_🧊_COOL_ZONE.py',label=':green[Click Me to get started with your quiz..!]',icon='🧊')
    
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    st.page_link("✍️_HOME.py", label=":rainbow[HOME]", icon="✍️")
with col2:
    st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")
with col3:
    st.page_link("pages/5_ℹ️_ABOUT.py", label=":rainbow[ABOUT]", icon="ℹ️")
with col4:
    st.page_link("pages/6_💬_CONTACT.py", label=":rainbow[CONTACT]", icon="💬")
with col5:
    st.page_link("pages/7_🤝_FEEDBACK.py", label=":rainbow[FEEDBACK]", icon="🤝")


    




