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
             background: url(" https://images3.alphacoders.com/134/1347726.png");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()
st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">CONTACT</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#09e65e;'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)
st.markdown("""<p style='font-size: 20px; text-align: center;color: #cc66ff;'>Data Science Enthusiast</p>""", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; text-align: center;'>Mobile: <a href='tel:6300006765'>6300006765</a></p>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; text-align: center;'>Email: <a href='mailto:saikiranpatnana5143@gmail.com'>saikiranpatnana5143@gmail.com</a></p>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; text-align: center;'>LinkedIn: <a href='https://www.linkedin.com/in/sai-kiran-patnana-55170a25b/'>Sai Kiran Patnana</a></p>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; text-align: center;'>GitHub: <a href='https://github.com/SAIKIRANPATNANA'>SAIKIRANPATNANA</a></p>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    st.page_link("✍️_HOME.py", label=":rainbow[HOME]", icon="✍️")
with col2:
    st.page_link("pages/5_ℹ️_ABOUT.py", label=":rainbow[ABOUT]", icon="ℹ️")
with col3:
    st.page_link("pages/7_🤝_FEEDBACK.py", label=":rainbow[FEEDBACK]", icon="🤝")
with col4:
    st.page_link("pages/1_✒️_MCQ.py", label=":rainbow[MCQ]", icon="✒️")
with col5:
    st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")

