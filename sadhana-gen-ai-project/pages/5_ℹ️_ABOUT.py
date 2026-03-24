import streamlit as st 
from integrator import *
import time

css = """
<style>
.rainbow-title-text{
    background: -webkit-linear-gradient(45deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 50px; 
    font-weight: bold;
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
             background: url("https://wallpapercave.com/uwp/uwp3008383.jpeg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()
st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">ABOUT</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#9dfc03;'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)

import streamlit as st

st.markdown("<h2 style='color:#0000cc;text-align:center;'>What Is Project Saadhana?</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Project Saadhana is your tool for self-assessment, effortlessly gauging your knowledge with just a few clicks.</i></p>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#00cc00;text-align:center;'>Why To Choose Project Saadhana?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Project Saadhana empowers you to evaluate your skills and determine your proficiency levels.</i></p>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#cc0000;text-align:center;'>How To Utilize Project Saadhana?</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;'>Step 1: Upload Your Content</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Begin by uploading your study materials or content PDF on the homepage.</i></p>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;'>Step 2: Choose Assessment Type</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Select the type of assessment you wish to undertake.</i></p>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;'>Step 3: Select Subject Context</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Choose the subject context on which you want to be quizzed.</i></p>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;'>Step 4: Set Difficulty Level</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Specify the difficulty level of the questions you want to attempt.</i></p>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;',>Step 5: Answer Questions</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Provide your answers to the quiz questions.</i></p>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ff33cc;text-align:center;'>Step 6: Submit and View Results</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><i>Click on submit to know the result of the quiz and view feedback on your performance.</i></p>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    st.page_link("✍️_HOME.py", label=":rainbow[HOME]", icon="✍️")
with col2:
    st.page_link("pages/6_💬_CONTACT.py", label=":rainbow[CONTACT]", icon="💬")
with col3:
    st.page_link("pages/7_🤝_FEEDBACK.py", label=":rainbow[FEEDBACK]", icon="🤝")
with col4:
    st.page_link("pages/1_✒️_MCQ.py", label=":rainbow[MCQ]", icon="✒️")
with col5:
    st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")

