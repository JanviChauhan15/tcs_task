import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_PATH = "data/policies"
CHROMA_PATH = "data/chroma_db"

def main():
    # Check if Groq API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set.")
        return

    # Clear existing vector store if it exists (since embeddings are changing)
    if os.path.exists(CHROMA_PATH):
        print(f"Removing existing vector store at {CHROMA_PATH}...")
        shutil.rmtree(CHROMA_PATH)

    # Load documents
    print(f"Loading documents from {DATA_PATH}...")
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    if not documents:
        print("No documents found.")
        return
    print(f"Loaded {len(documents)} documents.")

    # Split text
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # Create embeddings and store in Chroma
    print("Creating embeddings and storing in Chroma...")
    # Using HuggingFace Embeddings (Free, runs locally)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Chroma
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    print(f"Documents ingested successfully into {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
