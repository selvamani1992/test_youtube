from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from transcript import extract_video_id, get_youtube_transcript
import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st

api_key = st.secrets["Gemini_API_Key_3"]
import warnings
warnings.filterwarnings("ignore")


#------------------------------Initialization------------------------------#

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=api_key
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

#--------------------------------Indexing--------------------------------#

def chunk(transcripted_data):
    doc=Document(
    page_content=transcripted_data
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        separators=[" "],
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )

    rec_chunks = recursive_splitter.split_documents([doc])
    return rec_chunks

def indexing(video_url):
    video_id = extract_video_id(video_url)
    transcripted_data = get_youtube_transcript(video_id)
    rec_chunks = chunk(transcripted_data)    
    vector_db = FAISS.from_documents(
        rec_chunks,
        embeddings)
    return(vector_db)

#--------------------------------Retrieval--------------------------------#

def generate_answer(vector_db, query):
    result = vector_db.similarity_search(query, k = 3)

    context = "\n\n".join([doc.page_content for doc in result])

    prompt_template = f"""

        You are a helpful assistant answering questions using the provided context.

        Context:
        {context}

        Question:
        {query}

        Answer the question using only the provided context.
        if there is no relevant answere based on context, then say 'Information Unavailable'

        * Try to give short answer
        * Do not use any other information
        * Do not include any preamble or suffix in the answer
        * Give me the answer in less than 200 words
    """
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )

    final_prompt = prompt_template.format(
        context=context,
        question=query
    )
    response = llm.invoke(final_prompt)
    return(response.content)
