from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

load_dotenv()

FILE_PATH = os.environ.get("FILE_PATH","./base_knowledge/ricettario.pdf")
MODEL = os.environ.get("MODEL","gpt-4o-mini")

try:
    with open("prompt.txt", "r", encoding='utf-8') as f:
        PROMPT = f.read()
except FileNotFoundError:
    print("Prompt file not found. Please ensure 'prompt.txt' exists.")
    exit(1)  # Exit gracefully

loader = PyPDFLoader(FILE_PATH)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

class RAG():
    def __init__(self,retriever, prompt, model):
        self.retriever = retriever
        self.llm = ChatOpenAI(model=model)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("human", "{input}"),
            ]
        )
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(retriever, self.question_answer_chain)
    
    def invoke(self,text):
        results = self.rag_chain.invoke({"input": text})
        return results
    
rag = RAG(retriever, PROMPT, MODEL)