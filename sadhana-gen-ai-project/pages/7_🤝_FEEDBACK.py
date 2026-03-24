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
             background: url("https://wallpapercave.com/wp/fBhxQDf.jpg");
             background-size: cover
         }}
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

set_bg_hack_url()
st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">FEEDBACK</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#35ccc7'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)

if 'username' not in st.session_state:
    st.session_state['username'] = None
    st.session_state['feedback'] = None
    st.session_state['mobile'] = None

if 'credit' not in st.session_state:
    st.session_state['credit'] = 0
   
st.session_state.username = st.text_input("Enter Your Name Here:", placeholder="Your Name")
st.session_state.feedback = st.text_area("Enter Your Feedback Here:", height=150, placeholder="Your Feedback")
st.session_state.mobile = st.text_input("Enter Your Transaction Mobile Number Here:", placeholder="Your Transaction Mobile Number")

if st.button("Submit Feedback", key="feedback_button"):
    if st.session_state.username == None or st.session_state.username == "":
        st.error('Please Enter Your Name...!')
    elif st.session_state.feedback == None or st.session_state.feedback == "":
        st.error('Please Enter Your Feedback...!')
    elif st.session_state.mobile == None or st.session_state.mobile == "":
        st.error('Please Enter Your Transation Mobile Number...!')
    else:
        result = None
        with st.spinner("Your Feedback is getting submitted..!"):
            st.warning("Don't exit Project Saadhana until your feedback submission is successful..!")
            output = send_feedback({'username':st.session_state.username,'feedback':st.session_state.feedback, 'mobile': st.session_state.mobile})
            if(output!=-1):
                result = output
            else: 
                st.warning('Sorry, Something went wrong..!',icon="✍️")
                st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                exit()
        if result:
            st.info(f"Your achieved credit is {st.session_state.credit} ⭐. ")
            st.session_state.credit = 0
            st.success(f"🚀 :rainbow[Your Feedback has been successfully submitted. Thanks for your valuable feedback {st.session_state.username}!] 🙏")
        else:
            st.success("You have already submitted your feedback..!")

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    st.page_link("✍️_HOME.py", label=":rainbow[HOME]", icon="✍️")
with col2:
    st.page_link("pages/5_ℹ️_ABOUT.py", label=":rainbow[ABOUT]", icon="ℹ️")
with col3:
    st.page_link("pages/6_💬_CONTACT.py", label=":rainbow[CONTACT]", icon="💬")
with col4:
    st.page_link("pages/1_✒️_MCQ.py", label=":rainbow[MCQ]", icon="✒️")
with col5:
    st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")


