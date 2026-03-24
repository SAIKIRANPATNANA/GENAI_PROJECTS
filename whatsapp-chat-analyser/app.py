import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import random
from preprocessing import preprocess
from helping import fetch_stats,fetch_activesusers,fetch_topchatwords,fetch_topchatemojis,fetch_messagesbymonthyear,fetch_wordcloud,fetch_messagesbydate,fetch_messagesbymonth,fetch_messagesbyday,fetch_chatactivityheatmap
st.sidebar.title('Whatsapp Chat Analysis')
uploaded_file = st.sidebar.file_uploader('Chosse a file: ')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocess(data)
    # st.dataframe(df)
    userlist = df['users'].unique().tolist()
    # userlist.remove('group_notification')
    userlist.sort()
    userlist.insert(0,'Overall')
    selected_user = st.sidebar.selectbox('Show analysis wrt', userlist)
    if st.sidebar.button('Show Analysis'):
        # if(selected_user!='Overall'):
        st.dataframe(df[df['users']==selected_user])
        num_messages,num_words,num_media,num_urls,num_emojis,most_common_words,most_common_emojis = fetch_stats(selected_user,df)
        # st.title('Basic chat stats')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Basic Chat Stats</h1>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.title('Total Texts')
            st.header(num_messages)
        with col2:
            st.title('Total Words')
            st.header(num_words)
        with col3:
            st.title('Total Media')
            st.header(num_media)
        with col4:
            st.title('Total Urls')
            st.header(num_urls)
        with col5:
            st.title('Total Emojis')
            st.header(num_emojis)
        # st.title('Most Common Words')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Most Common Words</h1>", unsafe_allow_html=True)
        if(not(len(most_common_words))):
            st.header('NILL')
        else:
            for word in most_common_words:
                st.header(word)
        # st.title('Most Common Emojis')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Most Common Emojis</h1>", unsafe_allow_html=True)
        if(not(len(most_common_emojis))):
            st.header('NILL')
        else:
            for emoji in most_common_emojis:
                st.header(emoji)
        # st.title('Word Cloud')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Word Cloud</h1>", unsafe_allow_html=True)
        plotpath = fetch_wordcloud(selected_user,df)
        st.image(plotpath)
        if selected_user == 'Overall':
        # st.title('Most Active Users')
            st.markdown("<h1 style='text-align: center; color: Blue;'>Most Active Users</h1>", unsafe_allow_html=True)
            df1,plotpath = fetch_activesusers(df)
            st.image(plotpath)
            st.dataframe(df1)
        # st.title('Overall Chat activity by yearmonth')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Overall Chat Activity By Month and Year</h1>", unsafe_allow_html=True)
        df1,plotpath = fetch_messagesbymonthyear(selected_user,df)
        st.image(plotpath)
        st.dataframe(df1)
        # st.title('Overall Chat activity by date')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Overall Chat Activity By Date</h1>", unsafe_allow_html=True)
        df1,plotpath = fetch_messagesbydate(selected_user,df)
        st.image(plotpath)
        st.dataframe(df1)
        # st.title('Overall Chat activity by month')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Overall Chat Activity By Month</h1>", unsafe_allow_html=True)
        df1,plotpath = fetch_messagesbymonth(selected_user,df)
        st.image(plotpath)
        st.dataframe(df1)
        # st.title('Overall Chat activity by day')
        st.markdown("<h1 style='text-align: center; color: Blue;'>Overall Chat Activity By Day</h1>", unsafe_allow_html=True)
        df1,plotpath = fetch_messagesbyday(selected_user,df)
        st.image(plotpath)
        st.dataframe(df1)
        if selected_user=='Overall':
            # st.title('Chat Activit By Hour')
            st.markdown("<h1 style='text-align: center; color: Blue;'>Chat Activity By Hour</h1>", unsafe_allow_html=True)
            plotpath = fetch_chatactivityheatmap(selected_user,df)
            st.image(plotpath)
            # st.title('Top chat words')
            st.markdown("<h1 style='text-align: center; color: Blue;'>Top Chat Words</h1>", unsafe_allow_html=True)
            df2,plotpath = fetch_topchatwords(selected_user,df)
            st.image(plotpath)
            st.dataframe(df2)
            # st.title('Top chat emojis')
            st.markdown("<h1 style='text-align: center; color: Blue;'>Top Chat Emojis</h1>", unsafe_allow_html=True)
            df3,plotpath = fetch_topchatemojis(selected_user,df)
            st.image(plotpath)
            st.dataframe(df3)
        
        
    





        
        

    
    
