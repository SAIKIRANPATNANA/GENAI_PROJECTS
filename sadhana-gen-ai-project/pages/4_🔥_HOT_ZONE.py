import streamlit as st
from integrator import *
import time
import random
import importlib

@st.cache_data
def evaluate_qa_cacher(cleaned_answers,user_answers):
    try:
        output = evaluate_qa(cleaned_answers,user_answers)
        if(output!=-1):
            return output
        else:
            return -1
    except Exception as e:
        print(e)
        return -1

def check_answer(q):
    act_ans = st.session_state.cleaned_answers[q]
    usr_ans = st.session_state.user_answers[q]
    if act_ans == 'a':
        i = 1
    elif act_ans == 'b':
        i = 2
    elif act_ans == 'c':
        i = 3
    else:
        i = 4
    if usr_ans == 'a':
        j = 1
    elif usr_ans == 'b':
        j = 2
    elif usr_ans == 'c':
        j = 3
    else:
         j = 4
    return st.session_state.cleaned_questions[q][0],st.session_state.cleaned_questions[q][i],st.session_state.cleaned_questions[q][j]

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
             background: url("https://img.freepik.com/free-vector/gradient-black-background-with-wavy-lines_23-2149151738.jpg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack_url()
st.markdown(css, unsafe_allow_html=True)
rainbow_title_html = """<p class="rainbow-title-text">Hot Zone</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)
st.markdown("""<h5 style='font-size:25px;text-align:center;color:#ed1a1a;'><i>Developed By Sai Kiran  For Project Saadhana</i></h5>""", unsafe_allow_html=True)

if 'credit' not in st.session_state:
    st.session_state['credit'] = 0

if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file == None:
    if 'uploaded_file' not in st.session_state :
        st.session_state['uploaded_file'] = None
    st.warning('Kindly upload your content pdf on the Home page..!', icon="⚠️")
    st.page_link("✍️_HOME.py", label=":rainbow[Click Me to go to HOME..!]", icon="✍️")

else:

    if st.session_state.mode == 'objective' and st.session_state.user_answers is not None:
        st.markdown("<h4 style='color:#13e3f2;'>Quiz Result</h4>",unsafe_allow_html=True)
        output1,output2 = evaluate_mcq(st.session_state.cleaned_answers,st.session_state.user_answers)
        if(output1!=-1 and output2!=-1):
            score,wrong_answers = output1,output2
        else:
            st.warning('Sorry, Something went wrong..!',icon="✍️")
            st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
            exit()
        st.session_state.credit = score
        if score>8:
            st.success('Your have scored '+str(score)+'⭐.')
            st.info('Excellent, You just rocked the quiz.')
        elif score>5:
            st.success('Your have scored '+str(score)+'⭐.')
            st.info('Good Performance, You have given a nice attempt.')
        else:
            st.error('Your have scored '+str(score)+'⭐.')
            st.info("Hold the spirit, Try next time for best score.")
        if st.button("Check Answers"):
            for i in wrong_answers:
                question,act_ans,usr_ans = check_answer(i)
                st.write(question)
                st.error(usr_ans, icon="❌")
                st.success(act_ans,icon="✅")
                st.divider()

    elif st.session_state.mode == 'descriptive' and st.session_state.user_answers is not None:
        st.markdown("<h4 style='color:#13e3f2;'>Quiz Result</h4>",unsafe_allow_html=True)
        with st.status('Evaluation is in progress..!'):
            output = evaluate_qa_cacher(st.session_state.cleaned_answers,st.session_state.user_answers)
            if(output!=-1):
                scores = output 
            else:
                st.warning('Sorry, Something went wrong..!',icon="✍️")
                st.info('Kindly reload Saadhana and then try again..!',icon ='🧎🏽')
                exit()

        for i in range(5):
            if scores[i]>0.9:
                scores[i] = 2
            elif scores[i]>0.7:
                scores[i] = 1
            else:
                scores[i] = 0
        score = sum(scores)
        st.session_state.credit = score
        if score>7:
            st.success('Your have scored '+str(score)+'⭐.')
            st.info('Excellent, You just rocked the quiz.')
        elif score>5:
            st.success('Your have scored '+str(score)+'⭐.')
            st.info('Good Performance, You have  a nice attempt.')
        else:
            st.error('Your have scored '+str(score)+'.')
            st.info("Hold the spirit, Try next time for best score.")
        if st.button("Check Answers"):
            for i in range(5):
                question,ref_ans,usr_ans = st.session_state.cleaned_questions[i],st.session_state.cleaned_answers[i],st.session_state.user_answers[i]
                st.write(question)
                if(scores[i]==2):
                    st.subheader(':rainbow[Your Answer]')
                    st.success(usr_ans, icon="✅")
                    st.subheader(':rainbow[Reference Answer]')
                    st.success(ref_ans,icon="✅")
                elif(scores[i]==1):
                    st.subheader(':rainbow[Your Answer]')
                    st.info(usr_ans, icon="☑️")
                    st.subheader(':rainbow[Reference Answer]')
                    st.success(ref_ans,icon="✅")
                else:
                    st.subheader(':rainbow[Your Answer]')
                    if usr_ans == '':
                        st.error("NOT ATTEMPTED..!", icon="❌")
                    else:
                        st.error(usr_ans, icon="❌")
                    st.subheader(':rainbow[Reference Answer]')
                    st.success(ref_ans,icon="✅")
                st.divider()

    random = random.randint(1,1000)
    while(random==st.session_state.random):
        random = random.randint(1,1000)
    st.session_state.random = random
    
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


    
