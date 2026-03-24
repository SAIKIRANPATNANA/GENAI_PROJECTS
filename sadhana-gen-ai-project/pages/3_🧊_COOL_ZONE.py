import streamlit as st 
from integrator import *
import time

if 'snow_fall' not in st.session_state:
    st.session_state['snow_fall'] = None
    st.snow()
    

@st.cache_data
def get_mcq_general_cacher(text,difficulty_level,random):
    try: 
        output1,output2 = get_mcq_general(st.session_state.text,st.session_state.difficulty_level)
        if(output1!=0 and output2!=0):
            cleaned_questions,cleaned_answers = output1,output2
            return cleaned_questions,cleaned_answers
        else:
            return 0,0
    except Exception as e:
        print(e)
        return 0,0

@st.cache_data
def get_mcq_specific_cacher(topic_name,difficulty_level,random):
    try:
        output1,output2 = get_mcq_specific(topic_name,difficulty_level)
        if(output1!=0 and output2!=0):
            cleaned_questions,cleaned_answers = output1,output2
            return cleaned_questions,cleaned_answers
        else:
            return 0,0
    except Exception as e:
        print(e)
        return 0,0

@st.cache_data
def get_qa_general_cacher(text,difficulty_level,random):
    try:
        output1,output2 = get_qa_general(text,difficulty_level)
        if(output1!=0 and output2!=0):
            cleaned_questions,cleaned_answers = output1,output2
            return cleaned_questions,cleaned_answers
        else:
            return 0,0
    except Exception as e:
        print(e)
        return 0,0

@st.cache_data
def get_qa_specific_cacher(topic_name,difficulty_level,random):
    try:
        output1,output2 = get_qa_specific(st.session_state.topic_name,st.session_state.difficulty_level)
        if(output1!=0 and output2!=0):
            cleaned_questions,cleaned_answers = output1,output2
            return cleaned_questions,cleaned_answers
        else:
            return 0,0
    except Exception as e:
        print(e)
        return 0,0

st.markdown(
    """<style>
div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 18px;
}
    </style>
    """, unsafe_allow_html=True)
                
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
    
st.markdown(
    """<style>
div[class*="stTextArea"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 18px;
}
    </style>
    """, 
unsafe_allow_html=True)

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
             background: url("https://e1.pxfuel.com/desktop-wallpaper/158/660/desktop-wallpaper-black-backgrounds-black-website-background.jpg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()

st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">Cool Zone</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#00ccff;'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)

if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file == None:
    if 'uploaded_file' not in st.session_state :
        st.session_state['uploaded_file'] = None
    st.warning('Kindly upload your content pdf on the Home page..!', icon="⚠️")
    st.page_link("✍️_HOME.py", label=":rainbow[Click Me to go to HOME..!]", icon="✍️")

if 'flag' not in st.session_state:
    st.session_state['flag'] = 1

if st.session_state.uploaded_file is not None and st.session_state.topic_name is not None and st.session_state.difficulty_level is not None and st.session_state.text is not None:
    
    if 'user_answers' not in st.session_state or st.session_state.user_answers is not None:
        if st.session_state.mode == 'objective':
            st.session_state.user_answers = [None]*10
        else:
            st.session_state.user_answers = [None]*5
    if 'cleaned_answers' not in st.session_state or st.session_state.cleaned_answers is not None:
        st.session_state.cleaned_answers = None
    if 'cleaned_questions' not in st.session_state or st.session_state.cleaned_questions is not None:
        st.session_state.cleaned_questions = None

    with st.status('Preparing Questions based on your preference..!'):
        st.write('Wakening the Model..')
        st.write('Getting Stuff from Model..')
        if st.session_state.mode == 'objective' and st.session_state.flag:
            if(st.session_state.topic_name=='overall'):
                output1,output2  = get_mcq_general_cacher(st.session_state.text,st.session_state.difficulty_level,st.session_state.random)
                if(output1!=0 and output2!=0):
                    st.session_state.cleaned_questions,st.session_state.cleaned_answers = output1,output2
                else:
                    st.warning('Sorry, Something went wrong..!',icon="⚠️")
                    st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                    exit()
            else:
                output1,output2 =  get_mcq_specific_cacher(st.session_state.topic_name,st.session_state.difficulty_level,st.session_state.random)
                if(output1!=0 and output2!=0):
                    st.session_state.cleaned_questions,st.session_state.cleaned_answers =  output1,output2
                else:
                    st.warning('Sorry, Something went wrong..!',icon="⚠️")
                    st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                    exit()

        elif(st.session_state.mode=='descriptive' and st.session_state.flag):
            if(st.session_state.topic_name=='overall'):
                output1,output2 = get_qa_general_cacher(st.session_state.text,st.session_state.difficulty_level,st.session_state.random)
                if(output1!=0 and output2!=0):
                    st.session_state.cleaned_questions,st.session_state.cleaned_answers = output1,output2
                else:
                    st.warning('Sorry, Something went wrong..!',icon="⚠️")
                    st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                    exit()
            else:
                output1,output2 = get_qa_specific_cacher(st.session_state.topic_name,st.session_state.difficulty_level,st.session_state.random)
                if(output1!=0 and output2!=0):
                    st.session_state.cleaned_questions,st.session_state.cleaned_answers = output1,output2
                else:
                    st.warning('Sorry, Something went wrong..!',icon="⚠️")
                    st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                    exit()

        st.write('About To be Successful')
        st.write('Done')

    st.success('Questions are ready to be displayed..!')

    start_quiz = st.toggle('Start Quiz')
    if start_quiz:
        if st.session_state.mode == 'objective':
            for i in range(10):
                if(i):
                    st.divider()
                q = st.session_state.cleaned_questions[i]
                user_option = st.radio(q[0],[q[1],q[2],q[3],q[4]])
                if user_option == q[1]:
                    st.session_state.user_answers[i] = 'a'
                elif user_option == q[2]:
                    st.session_state.user_answers[i] = 'b'
                elif user_option == q[3]:
                    st.session_state.user_answers[i] = 'c'
                else:
                    st.session_state.user_answers[i] = 'd'
            st.info('Once cross check your answers before clicking submit button.!')
            if st.button('Submit Quiz') :
                st.page_link("pages/4_🔥_HOT_ZONE.py", label=":green[Click Me to see your quiz result..!]", icon="🔥")
        elif st.session_state.mode == 'descriptive':
            for i in range(5):
                if i:
                    st.divider()
                q = st.session_state.cleaned_questions[i]
                st.session_state.user_answers[i] = st.text_area(q,'',key=i,help='Type your answer in the text box provided below..')
            st.info('Once verify your answers before clicking submit button.!')
            if st.button('Submit Quiz'):
                st.page_link("pages/4_🔥_HOT_ZONE.py", label=":green[Click Me to see your quiz result..!]", icon="🔥")

    col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,1])
    with col1:
        st.page_link("✍️_HOME.py", label=":rainbow[HOME]", icon="✍️")
    with col2:
        st.page_link("pages/1_✒️_MCQ.py", label=":rainbow[MCQ]", icon="✒️")
    with col3:
        st.page_link("pages/2_📝_Q&A.py", label=":rainbow[Q&A]", icon="📝")
    with col4:
        st.page_link("pages/7_🤝_FEEDBACK.py", label=":rainbow[FEEDBACK]", icon="🤝")
    with col5:
        st.page_link("pages/5_ℹ️_ABOUT.py", label=":rainbow[ABOUT]", icon="ℹ️")
    with col6:
        st.page_link("pages/6_💬_CONTACT.py", label=":rainbow[CONTACT]", icon="💬")







                
                    
                        
                
                
                
                




        





