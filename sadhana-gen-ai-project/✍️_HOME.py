import streamlit as st
from integrator import *
import base64

@st.cache_data
def get_pdf_text_n_vector_store_cacher(uploaded_file):
    try:
        output = get_pdf_text(uploaded_file)
        if(output!=0):
            text = output
            if(create_vector_store(text)):
                return text
            else:
                return 0
        else:
            return 0
    except Exception as e:
        print(e)
        return 0

def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------url
    The background.
    '''
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("https://images8.alphacoders.com/132/1325725.png");
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


st.set_page_config(
    page_title="Project Saadhana",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed",
) 

set_bg_hack_url()

st.balloons()

css = """
<style>
hr {
    color: white; 
    background-color: #ACF121; 
    height: 2px; 
    border: none;
}
.rainbow-title-text{
    background: -webkit-linear-gradient(45deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 50px; 
    font-weight: bold;
    text-align: center;
    animation: rainbow-text-animation 15s ease infinite;
}
.rainbow-developer-text{
    background: -webkit-linear-gradient(45deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 30px; 
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

st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">Project Saadhana Welcomes You!</p>"""
rainbow_developer_html = """<p class="rainbow-developer-text"><i>Ideated & Developed By Sai Kiran Patnana</i></p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h3 style='text-align:center;color:#13D1B7 ;'><i> - A Gen AI Based Quiz Application</i></h3>""", unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown(rainbow_developer_html, unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

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

if 'uploaded_file'  not in st.session_state:
    st.session_state['uploaded_file'] = None
    st.session_state['mode'] = None
    st.session_state['text'] = None
    

if  st.session_state.uploaded_file == None:
    st.session_state.uploaded_file = st.file_uploader("Choose any Study Material PDF of your choice here...")

if st.session_state.uploaded_file is not None:
    if st.button('Add New Content'):
        st.session_state.uploaded_file = st.file_uploader("Choose any Study Material PDF of your choice here...")
    else:
        with st.spinner('Processing your uploaded content, it takes time based on your uploaded filesize!'):
            output = get_pdf_text_n_vector_store_cacher(st.session_state.uploaded_file)
            if(output!=0):
                st.session_state.text = output
            else:
                st.error('Your uploaded file is not a valid PDF file..!',icon="⚠️")
                st.info('Kindly reload Saadhana and then upload a valid PDF file..!',icon ='🧎🏽')
                exit()
        st.success('Preprocessing is successful..!')
        choice = st.radio("Choose a Quiz Type", [":rainbow[Objective]", ":rainbow[Descriptive]"], captions = ["You need to choose one option from given four options.", "You need to write answers to theoretical questions."])
        if choice == ":rainbow[Objective]":
            st.session_state.mode = 'objective'
            st.page_link("pages/1_✒️_MCQ.py", label=":green[Click Me To Try Objective Quiz...!]", icon="✒️")
        else:
            st.session_state.mode = 'descriptive'
            st.page_link("pages/2_📝_Q&A.py", label=":green[Click Me To Try Descriptive Quiz...!]", icon="📝")

col1, col2, col3, col4, col5  = st.columns([1,1,1,1,1])
with col1:
    st.page_link("pages/5_ℹ️_ABOUT.py", label=":rainbow[ABOUT]", icon="ℹ️")
with col2:
    st.page_link("pages/6_💬_CONTACT.py", label=":rainbow[CONTACT]", icon="💬")
with col3:
    st.page_link("pages/7_🤝_FEEDBACK.py", label=":rainbow[FEEDBACK]", icon="🤝")
with col4: 
    st.page_link("pages/1_✒️_MCQ.py", label=":rainbow[MCQ]", icon="✒️")
with col5:
    st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")

