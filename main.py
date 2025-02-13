import os
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import ssl
import nltk
import sqlite3
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

persist_directory = "./embeddings/chromadb"


def get_url_by_hash(hash):
    conn = sqlite3.connect('data.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE hash = ?", (hash,))
    row = cursor.fetchone()
    return row["link"]


def download_punkt_method():
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        if 'punkt' not in nltk.data.find('tokenizers/'):
            nltk.download('punkt')
            print("Download complete.")
        else:
            print("'punkt' corpus already downloaded.")
    except Exception as e:
        print(f"Error downloading 'punkt' corpus: {e}")


def add_embeddings_to_chromadb(html_dir):
    download_punkt_method()
    db_files_exist = os.path.exists(os.path.join(persist_directory, "chroma.sqlite3"))
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
    if db_files_exist:
        print("Loading existing ChromaDB...")
        db = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    else:
        print("Creating a new ChromaDB...")

        documents = []
        for filename in os.listdir(html_dir):
            if filename.endswith(".html"):
                try:
                    loader = UnstructuredHTMLLoader(os.path.join(html_dir, filename))
                    doc = loader.load()[0]
                    documents.append(doc)
                except BaseException:
                    print(f"ERROR in file: {filename}")

        text_splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=100)
        texts = []
        metadatas = []
        for doc in documents:
            splits = text_splitter.split_text(doc.page_content)
            texts.extend(splits)
            metadatas.extend([{"source": os.path.splitext(doc.metadata["source"])[0].split("/")[-1]}] * len(splits))

        db = Chroma.from_texts(texts=texts, embedding=embeddings, persist_directory="./embeddings/chromadb")

        db.add_texts(texts=texts, metadatas=metadatas)
    return db


def get_insights(db, question):
    llm = Ollama(model="phi3")
    similar_snippets = db.similarity_search_with_score(question, k=5)
    sources = set()
    for snippet in similar_snippets:
        try:
            source = get_url_by_hash(snippet[0].metadata["source"])
            sources.add(source)
        except KeyError:
            print("Sources not found")
    context = "\n".join([snippet[0].page_content for snippet in similar_snippets])
    llm = OllamaFunctions(model="phi3", format="json", temperature=0)
    insights = llm.invoke(
        f"Your are Alex, an AI sales executive at Cognitus. Using the provided context:{context}, please answer the following question: {question}")

    return insights.content, sources


html_dir = "./data/crawled_html_copy/"
db = add_embeddings_to_chromadb(html_dir)


@app.post("/get_insights")
def get_insights_endpoint(body: dict = Body(...)):
    target_text = body.get("target_text")
    if target_text is None:
        return {"detail": "target_text is required"}

    response, sources = get_insights(db, target_text)
    return {"response": response, "sources": sources}
