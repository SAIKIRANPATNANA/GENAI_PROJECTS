from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import warnings as warn
warn.filterwarnings("ignore")
from langchain_groq import ChatGroq
import os
HF_TOKEN = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
if not HF_TOKEN:
    raise ValueError('Set HF_TOKEN or HUGGINGFACE_TOKEN before running this project.')
os.environ['HF_TOKEN'] = HF_TOKEN
from langchain_community.vectorstores import FAISS
def save_bos_to_db(file_path):
    loader=PyPDFLoader(file_path)
    docs=loader.load()
    print(docs)
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=15000,chunk_overlap=3000)
    final_documents=text_splitter.split_documents(docs)
    print(final_documents)
    embeddings =HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db=FAISS.from_documents(docs,embeddings)
    print(db)
    db.save_local("faiss_index")
    return embeddings

def load_db_n_get_retriever(db_path,embeddings):
    db=FAISS.load_local(db_path,embeddings,allow_dangerous_deserialization=True)
    retriever=db.as_retriever()
    return retriever

def model_setup(model,api_key):
    llm = ChatGroq(model_name = model,groq_api_key = api_key)    
    return llm

def GetUnits(llm,retriever,subject):
  context = list()
  context.append(subject)
  docs1 = retriever.invoke(subject)
  docs1 = [doc.page_content.replace('\n', ' ') for doc in docs1]
  context.extend(docs1)
  print(context)
  class UnitNames(BaseModel):
      units: list = Field(..., description="Units Titles List")
  structured_llm = llm.with_structured_output(UnitNames)
  def get_unit_names(context: list) -> UnitNames:
      prompt_template = f"""
      context: {context[1:]}  # The context extracted from the provided board of studies document with respect to the subject {context[0]}
      Your Task:
        - Read the Context Carefully carefully.
        - Genarate the list of the titles of all the units present in the subject {context[0]}.
      Example Output:
      for the subject Web Technologies, 
      Output list of units shoule be like ['UNIT I: Introduction to Web World', 'UNIT II: Server Programming', 'UNIT III: Database Connectivity', 'UNIT IV: Front-End Web UI Frameworks and Tools', 'UNIT V: Bootstrap', 'UNIT VI: NodeJs']
      Response Format:
        {{
          "units": Give the list of all the units titles present in the subject {context[0]}
        }}

      """
      structured_response = structured_llm.invoke(prompt_template)
      return structured_response
  return get_unit_names(context).units

def GetTopics(llm,retriever,subject,unit):
  context = list()
  context.append(subject)
  context.append(unit)
  docs2 = retriever.invoke(unit)
  docs2 = [doc.page_content.replace('\n', ' ') for doc in docs2]
  context.extend(docs2)
  print(context)
  class TopicNames(BaseModel):
      topics: list = Field(..., description="Topics Names List")
  structured_llm = llm.with_structured_output(TopicNames)
  def get_topic_names(context: list) -> TopicNames:
      prompt_template = f"""
      context: {context[2:]}  # The context extracted from the provided board of studies document with respect to the unit name {context[1]} in the subject {context[0]}
      Your Task:
        - Read the Context Carefully carefully.
        - Genates the list of the names of all the topics present under the unit name {context[1]} in the subject {context[0]}.
      Example Output:
      for the unit statistics in the subject Maths,
      output of the topic names list should be like ['Descriptive statistics','Measures of central tendency', 'Measures of dispersion', 'Inferential statistics'])
      Response Format:
        {{
          "topics": Give the list of all the topic names present under the unit name {context[1]} in the subject {context[0]}.
        }}
      """
      structured_response = structured_llm.invoke(prompt_template)
      return structured_response
  return get_topic_names(context).topics

def getContent(model_name,api_key,subject,topic_name,student_level):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful teaching assistant capable of generating a very elaborated content with all the concepts in the markdown style for the topic {topic_name} in the subject {subject} to a student of of understanding level {student_level}. At the end of the content make sure to include minimum 5 to 6 questions of distinct types based on generated content to test the user.",
            )
        ]
    )

    llm = ChatGroq(
        model=model_name,
        temperature=0.5,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key

    )
    chain = prompt | llm
    response = chain.invoke(
        {   "subject":subject,
            "topic_name": topic_name,
            "student_level": student_level
        }
    )
    return response.content

def GetRevisionNotes(llm, content, topic_name):
    class RevisionNotes(BaseModel):
        points: list = Field(..., description="Revision Notes")
    
    structured_llm = llm.with_structured_output(RevisionNotes)
    
    def get_revision_notes(content: str) -> RevisionNotes:
        prompt_template = f"""
        content: {content}  # The content generated for the topic {topic_name}.
        Your Task:
          - Read the Content Carefully carefully.
          - Generate the list of quick revision notes points for the topic {topic_name}.
    
        Response Format:
          {{
            "points": Give the list of all the important points for the topic {topic_name} from the content.
          }}
        """
        structured_response = structured_llm.invoke(prompt_template)
        return structured_response
    
    return get_revision_notes(content).points

def save_content(content):
    with open('content.md', 'w+') as f:
        f.write(content)