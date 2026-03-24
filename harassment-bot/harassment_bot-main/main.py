import streamlit as st

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

set_bg_hack_url()

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
rainbow_title_html = """<p class="rainbow-title-text">Project SheildVerse!</p>"""
st.markdown(rainbow_title_html, unsafe_allow_html=True)


col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.page_link("pages/register_complaint.py", label=":rainbow[Complaint Registration]", icon="ℹ️")
with col2:
    st.page_link("pages/track_complaint_status.py", label=":rainbow[Complaint Status Tracking]", icon="🔍")
with col3:
    st.page_link("pages/admin_login.py", label=":rainbow[Admin Login]", icon="🔰")
