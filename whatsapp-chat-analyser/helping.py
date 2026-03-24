from urlextract import URLExtract
from collections import Counter
from wordcloud import WordCloud
from datetime import datetime
import string
import emoji
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from stop_words import get_stop_words
stopwords = get_stop_words('en')
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"  
                           "]+", flags=re.UNICODE)
emojis = []
messages = []
def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users']==selected_user]   
    emoji = [emoji_pattern.findall(msg) for msg in df['messages']]
    global emojis
    global messages
    for moj in emoji:
        if(len(moj)>=1):
            li2 = []
            for i in range(len(moj)):
                for obj in moj[i]:
                    li2.append(obj)
            moj = li2
        emojis.extend(moj)  
    emojis = [emoji for emoji in emojis if emoji != '️']
    num_messages = len(df)
    df = df[df['users']!='group_notification']
    words = [word for msg in df['messages'] for word in msg.split() if msg!='<Media omitted>\n' and word not in emojis and word not in string.punctuation]
    word_counts = Counter(words)
    word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))
    most_common_words = [word for word in word_counts]
    if(len(most_common_words)>3):
        most_common_words = most_common_words[:3]
    num_words = len(words)
    num_media = len(df[df['messages']=='<Media omitted>\n'])
    num_emojis = len(emojis)
    emoji_counts = Counter(emojis)
    emoji_counts = dict(sorted(emoji_counts.items(), key=lambda item: item[1], reverse=True))
    most_common_emojis= [emoji for emoji in emoji_counts]
    if(len(most_common_emojis)>3):
        most_common_emojis = most_common_emojis[:3]
    extractor = URLExtract()
    num_urls = len([extractor.find_urls(msg)  for msg in  list(df['messages']) if len(extractor.find_urls(msg))!=0])
    messages = [msg for msg in df['messages'] if msg!='<Media omitted>\n']
    return num_messages,num_words,num_media,num_urls,num_emojis,most_common_words,most_common_emojis
def fetch_wordcloud(selected_user,df):
    global messages
    text = ' '.join(messages)
    wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=set(stopwords)).generate(text)
    plt.figure(figsize=(8, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plotpath = "word_cloud.png"
    plt.savefig(plotpath)
    plt.close()
    return plotpath
def fetch_messagesbymonthyear(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users']==selected_user]
    df1 = df.groupby(['year','month']).count()['messages'].reset_index()
    month_year = []
    for i in range(len(df1)):
        month_year.append(df1['month'][i]+'-'+str(df1['year'][i]))
    df1.drop(columns = ['year','month'],axis=1, inplace=True)
    df1['month_year'] = month_year
    message_counts = list(df1['messages'])
    plt.figure(figsize=(10,6))
    plt.plot(month_year,message_counts,color='green')
    plt.xlabel('month of year')
    plt.ylabel('number of messages')
    plt.title('number of messages by month')
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plotpath = "messages_by_month.png"
    plt.savefig(plotpath)
    plt.close()
    return df1,plotpath
def fetch_messagesbydate(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users']==selected_user]
    def reverse_date(date_str):
        date_str = date_str.strftime('%Y-%m-%d')
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    df['only_date'] = df['date'].apply(reverse_date)
    df1 = df.groupby(['only_date']).count()['messages'].reset_index()
    df1 = df1.rename({'only_date': 'date'},axis=1)
    message_counts = list(df1['messages'])
    dates = list(df1['date'])
    plt.figure(figsize=(9,6))
    plt.plot(dates,message_counts,color='blue')
    plt.xlabel('date')
    plt.ylabel('number of messages')
    plt.title('number of messages by date')
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plotpath = "messages_by_date.png"
    plt.savefig(plotpath)
    plt.close()
    return df1,plotpath
def fetch_messagesbymonth(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users']==selected_user]
    df1 = df.groupby(['month']).count()['messages'].reset_index()
    message_counts = list(df1['messages'])
    months = list(df1['month'])
    colors = sns.color_palette("hls", len(months))
    plt.figure(figsize=(10, 6))
    sns.barplot(x=months, y=message_counts, palette=colors)
    plt.xlabel('Month')
    plt.ylabel('Number of Messages')
    plt.title('Number of Messages by Month')
    plt.tight_layout()
    plotpath = "messages_by_month.png"
    plt.savefig(plotpath)
    plt.close()
    return df1,plotpath
def fetch_messagesbyday(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users']==selected_user]
    df['day'] = df['date'].dt.day_name()
    df1 = df.groupby(['day']).count()['messages'].reset_index()
    message_counts = list(df1['messages'])
    days = list(df1['day'])
    colors = sns.color_palette("hls", len(days))
    plt.figure(figsize=(10, 6))
    sns.barplot(x=days, y=message_counts, palette=colors)
    plt.xlabel('Day')
    plt.ylabel('Number of Messages')
    plt.title('Number of Messages by Day')
    plt.tight_layout()
    plotpath = "messages_by_day.png"
    plt.savefig(plotpath)
    plt.close()
    return df1,plotpath
def fetch_activesusers(df):
    df = df[df['users']!='group_notification']
    data = df['users'].value_counts()
    data1 = dict(data.head())
    users = list(data1.keys())
    message_counts = list(data1.values())
    colors = sns.color_palette("hls", len(users))
    plt.figure(figsize=(10, 6))
    sns.barplot(x=users, y=message_counts, palette=colors)
    plt.xlabel('Users')
    plt.ylabel('Number of Messages')
    plt.title('Number of Messages by User')
    plt.tight_layout()
    plotpath = "most_active_users.png"
    plt.savefig(plotpath)
    plt.close()
    data2 = dict(df['users'].value_counts())
    data2 = {'users':data2.keys(),'number of messages':data2.values()}
    df1 = pd.DataFrame(data2)
    return df1,plotpath
def fetch_topchatwords(selected_user,df):
    df = df[df['users']!='group_notification']
    if selected_user!='Overall':
        df = df[df['users']=='selected_user']
    words = [word for msg in df['messages'] for word in msg.split() if msg!='<Media omitted>\n' and word not in emojis and word not in string.punctuation]
    word_counts = Counter(words)
    word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))
    data = {'chat_words': word_counts.keys(), 'word_frequency':word_counts.values()}
    chat_words = list(word_counts.keys())
    word_frequency = list(word_counts.values())
    df1 = (pd.DataFrame(data))[:25]
    colors = sns.color_palette("hls", 25)
    plt.figure(figsize=(7, 6))
    sns.barplot(x=word_frequency[:25], y=chat_words[:25], palette=colors)
    plt.xlabel('frequency')
    plt.ylabel('words')
    plt.title('chat word frequency')
    plt.tight_layout()
    plotpath = "chatwordfrequency.png"
    plt.savefig(plotpath)
    plt.close()
    return df,plotpath
def fetch_chatactivityheatmap(selected_user,df):
    df = df[df['users']!='group_notification'].reset_index()
    if selected_user!='Overall':
        df = df[df['users']=='selected_user'].reset_index()
    df['day_name'] = df.date.dt.day_name()
    df['period'] = 0
    for i in range(len(df)):
        if(df['hour'][i]==0):
            df['period'][i] = '00 - 1'
        elif(df['hour'][i]==23):
            df['period'][i] = '23 - 00'
        else:
            df['period'][i] = str(df['hour'][i]) + ' - ' + str(df['hour'][i]+1)
    hm = df.pivot_table(index='day_name',columns='period',values='messages',aggfunc='count').fillna(0)
    plt.figure(figsize=(6, 6))
    sns.heatmap(hm, annot=True, cmap='viridis')
    plt.ylabel('Day')
    plt.xlabel('Hour')
    plt.title('Day Vs Hour Activity')
    plotpath = 'chatactivityheatmap.png'
    plt.savefig(plotpath)
    plt.close()
    return plotpath
def fetch_topchatemojis(selected_user,df):
    df = df[df['users']!='group_notification']
    if selected_user!='Overall':
        df = df[df['users']=='selected_user']
    global emojis
    emoji_counts = Counter(emojis)
    emoji_counts = dict(sorted(emoji_counts.items(), key=lambda item: item[1], reverse=True))
    data = {'chat_emojis': emoji_counts.keys(), 'emoji_frequency':emoji_counts.values()}
    chat_emojis = list(emoji_counts.keys())
    emoji_frequency = list(emoji_counts.values())
    df1 = (pd.DataFrame(data))[:25]
    colors = sns.color_palette("hls", 25)
    plt.figure(figsize=(7, 6))
    sns.barplot(x=emoji_frequency[:25], y=chat_emojis[:25], palette=colors)
    plt.xlabel('frequency')
    plt.ylabel('emojis')
    plt.title('chat emoji frequency')
    plt.tight_layout()
    plotpath = "chat_emoji_frequency.png"
    plt.savefig(plotpath)
    plt.close()
    return df1,plotpath
