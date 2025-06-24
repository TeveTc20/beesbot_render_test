from langchain_chroma import Chroma
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

url_path = "URL.txt"

if not os.path.exists(url_path):
    raise FileNotFoundError(f"txt file not found at {url_path}")

url_loader = TextLoader("URL.txt", encoding="utf-8")
url_pages = url_loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
url_page_split = text_splitter.split_documents(url_pages)
url_chroma_directory = "./chroma_url_db"
os.makedirs(url_chroma_directory, exist_ok=True)
vectorstore = Chroma.from_documents(
    documents=url_page_split,
    embedding=embeddings,
    persist_directory=url_chroma_directory,
    collection_name="URL"
)


url_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})