import warnings as warn 
warn.filterwarnings('ignore')
import os
import json
import requests
import random
from prompt_templates import *
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set")
os.environ["GOOGLE_API_KEY"] = google_api_key
genai.configure(api_key = os.environ['GOOGLE_API_KEY'])

def generate_mcq_specific(docs,prompt_template):
  try:
    model=ChatGoogleGenerativeAI(model='gemini-1.5-pro-latest',temperature=0.3)
    prompt=PromptTemplate(template=prompt_template,input_variables=['context'])
    chain=load_qa_chain(model,chain_type='stuff',prompt=prompt)
    response = chain.invoke(
      {"input_documents":docs},
      return_only_outputs=True
    )
    print(response['output_text'])
    return response['output_text']
  except Exception as e:
    print(e)
    return 0

def get_cleaned_mcq_specific(response,docs,prompt_template):
  try:
    questions_list = response.split('\n')
    for i in questions_list:
      if '' == i:
        questions_list.remove(i)
    answers = list()
    for i in questions_list:
      if 'Answer: ' in i:
        answers.append(i)
    questions_list_1 = list()
    i = 0
    while(i<len(questions_list)):
        q = list()
        j = 0
        while(j<5 and i<len(questions_list)):
            q.append(questions_list[i])
            i += 1
            j += 1
        i+=1
        questions_list_1.append(q)
    cleaned_questions = list()
    for question in questions_list_1:
      cleaned_question = list()
      for i in range(5):
        if(i==0):
          cleaned_question.append(question[i][question[i].find('.')+2:])
        else:
          cleaned_question.append(question[i][question[i].find(')')+2:])
      cleaned_questions.append(cleaned_question)
    cleaned_answers = list()
    for i in answers:
      cleaned_answers.append(i[i.find(':')+2:i.find(':')+3])
    return cleaned_questions,cleaned_answers
  except Exception as e:
    print(e)
    response = generate_mcq_specific(docs,prompt_template)
    return get_cleaned_mcq_specific(response,docs,prompt_template)


# def generate_mcq_general(cleaned_questions,cleaned_answers,chunks,difficulty_level):
#    try:
#       questions = []
#       context_choice_list = [i for i in range(len(chunks))]
#       for i in range(10):
#         random_number = random.choice(context_choice_list)
#         context_choice_list.remove(random_number)
#         context = chunks[random_number]
#         model = genai.GenerativeModel('gemini-1.5-pro-latest')
#         prompt_template = get_mcq_prompt_template_general(context,difficulty_level)
#         response = model.generate_content(prompt_template)
#         questions.append(response.text)
#       return questions
#    except:
#       return generate_mcq_general(cleaned_questions,cleaned_answers,chunks,difficulty_level)

# def get_cleaned_mcq_general(cleaned_questions,cleaned_answers,chunks,difficulty_level,response):
#   try:
#       for question in response:
#         question = question.split('\n')
#         for i in question:
#           if i=='':
#             question.remove(i)
#         for i in range(len(question)-1):
#           question[i] = question[i][question[i].index(')')+2:]
#         question[5] = question[5][question[5].index(':')+2:question[5].index(':')+3]
#         if(len(cleaned_questions)==10 and len(cleaned_answers)==10):
#           return cleaned_questions,cleaned_answers
#         cleaned_questions.append(question[:5])
#         cleaned_answers.append(question[5])
#       return cleaned_questions,cleaned_answers
#   except:
#     response = generate_mcq_general(cleaned_questions,cleaned_answers,chunks,difficulty_level)
#     if(len(cleaned_questions)==10 and len(cleaned_answers)==10):
#         return cleaned_questions,cleaned_answers
#     return get_cleaned_mcq_general(cleaned_questions,cleaned_answers,chunks,difficulty_level,response)

def generate_mcq_general(docs,difficulty_level):
  try:
      prompt_template = get_mcq_prompt_template_general(docs,difficulty_level)
      model = genai.GenerativeModel('gemini-1.5-pro-latest')
      response = model.generate_content(prompt_template)
      print(response.text)
      return response.text
  except Exception as e:
    print(e)
    return 0

def get_cleaned_mcq_general(response,docs,difficulty_level):
    try:
      questions_list = response.split('\n')
      for i in questions_list:
        if '' == i:
          questions_list.remove(i)
      answers = list()
      for i in questions_list:
        if 'Answer: ' in i:
          answers.append(i)
      questions_list_1 = list()
      i = 0
      while(i<len(questions_list)):
          q = list()
          j = 0
          while(j<5 and i<len(questions_list)):
              q.append(questions_list[i])
              i += 1
              j += 1
          i+=1
          questions_list_1.append(q)
      cleaned_questions = list()
      for question in questions_list_1:
        cleaned_question = list()
        for i in range(5):
          if(i==0):
            cleaned_question.append(question[i][question[i].find('.')+2:])
          else:
            cleaned_question.append(question[i][question[i].find(')')+2:])
        cleaned_questions.append(cleaned_question)
      cleaned_answers = list()
      for i in answers:
        cleaned_answers.append(i[i.find(':')+2:i.find(':')+3])
      return cleaned_questions,cleaned_answers
    except Exception as e:
      print(e)
      response = generate_mcq_general(docs,difficulty_level)
      return get_cleaned_mcq_general(response,docs,difficulty_level)

def generate_qa_specific(docs,prompt_template):
  try:
    model=ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",temperature=0.3)
    prompt=PromptTemplate(template=prompt_template,input_variables=['context'])
    chain=load_qa_chain(model,chain_type='stuff',prompt=prompt)
    response = chain.invoke(
      {"input_documents":docs},
      return_only_outputs=True
    )
    print(response['output_text'])
    return response['output_text']
  except Exception as e:
    print(e)
    return 0

def get_cleaned_qa_specific(response,docs,prompt_template):
  try:
    questions = response.split('\n')
    for i in questions:
      if i=='':
        questions.remove(i)
    questions_1 = [q for q in questions if 'Question:' in q]
    answers = [ans for ans in questions if 'Answer:' in ans]
    cleaned_questions = [q[q.index(':')+2: ] for q in questions_1]
    cleaned_answers = [ans[ans.index(':')+2: ] for ans in answers]
    return cleaned_questions,cleaned_answers
  except Exception as e:
    print(e)
    response = generate_qa_specific(docs,prompt_template)
    return get_cleaned_qa_specific(response,docs,prompt_template)

# def generate_qa_general(cleaned_questions,cleaned_answers,chunks,difficulty_level):
#   try:
#     questions = str()
#     context_choice_list = [i for i in range(len(chunks))]
#     for i in range(5):
#       random_number = random.choice(context_choice_list)
#       context_choice_list.remove(random_number)
#       context = chunks[random_number]
#       prompt_template = get_qa_prompt_template_general(context,difficulty_level)
#       model = genai.GenerativeModel('gemini-1.5-pro-latest')
#       response = model.generate_content(prompt_template)
#       questions += '\n'+response.text
#     return questions
#   except:
#     return generate_qa_general(cleaned_questions,cleaned_answers,chunks,difficulty_level)

# def get_cleaned_qa_general(cleaned_questions,cleaned_answers,chunks,difficulty_level,response):
#   try:
#     questions = response.split('\n')
#     for i in questions:
#       if i=='':
#         questions.remove(i)
#     questions_1 = [q for q in questions if 'Question:' in q]
#     answers = [ans for ans in questions if 'Answer:' in ans]
#     if(len(cleaned_questions)==5 and len(cleaned_answers)==5):
#       return cleaned_questions, cleaned_answers
#     ques_li = [q[q.index(':')+2: ] for q in questions_1]
#     ans_li = [ans[ans.index(':')+2: ] for ans in answers]
#     for i in range(5):
#       if(len(cleaned_questions)<5 and len(cleaned_answers)<5):
#         cleaned_questions.append(ques_li[i])
#         cleaned_answers.append(ans_li[i])
#     return cleaned_questions,cleaned_answers
#   except:
#     response = generate_qa_general(cleaned_questions,cleaned_answers,chunks,difficulty_level)
#     if(len(cleaned_questions)==5 and len(cleaned_answers)==5):
#         return cleaned_questions, cleaned_answers
#     return get_cleaned_qa_general(cleaned_questions,cleaned_answers,chunks,difficulty_level,response)

def generate_qa_general(docs,difficulty_level):
    try:
      prompt_template = get_qa_prompt_template_general(docs,difficulty_level)
      model = genai.GenerativeModel('gemini-1.5-pro-latest')
      response = model.generate_content(prompt_template)
      print(response.text)
      return response.text
    except Exception as e: 
      print(e)
      return 0

def get_cleaned_qa_general(response,docs,difficulty_level):
    try:
      questions = response.split('\n')
      for i in questions:
        if i=='':
          questions.remove(i)
      questions_1 = [q for q in questions if 'Question:' in q]
      answers = [ans for ans in questions if 'Answer:' in ans]
      cleaned_questions = [q[q.index(':')+2: ] for q in questions_1]
      cleaned_answers = [ans[ans.index(':')+2: ] for ans in answers]
      return cleaned_questions,cleaned_answers
    except Exception as e:
        print(e)
        response = generate_qa_general(docs,difficulty_level)
        return get_cleaned_qa_general(response,docs,difficulty_level)
