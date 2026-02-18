import os
import json
import time
from datetime import datetime
import hashlib
import shutil
from typing import List, Dict, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Constants
POLICIES_DIR = "data/policies"
CHROMA_PATH = "data/chroma_db"
STATE_FILE = "data/indexed_state.json"

# Ensure directories exist
os.makedirs(POLICIES_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

class PolicyEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embeddings
        )
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _get_doc_id(self, filename: str) -> str:
        """Generate a consistent ID based on filename."""
        return hashlib.md5(filename.encode()).hexdigest()

    def get_indexed_files(self) -> List[Dict]:
        """Return list of indexed files with metadata."""
        return list(self.state.values())

    def index_file(self, filename: str, file_path: Optional[str] = None) -> Dict:
        """
        Index a single PDF file.
        1. Load PDF
        2. Chunk
        3. Delete old chunks for this doc_id
        4. Insert new chunks
        5. Update state
        """
        if not file_path:
            file_path = os.path.join(POLICIES_DIR, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        doc_id = self._get_doc_id(filename)
        print(f"Indexing {filename} (Doc ID: {doc_id})...")

        # 1. Load
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        if not docs:
            return {"status": "error", "message": "No content found in PDF"}

        # 2. Chunk
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(docs)

        # 3. Enrich Metadata
        timestamp = datetime.now().isoformat()
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "doc_id": doc_id,
                "doc_name": filename,
                "chunk_id": f"{doc_id}_{i}",
                "indexed_at": timestamp,
                "page": chunk.metadata.get("page", 0) + 1 # 1-based
            })
            enriched_chunks.append(chunk)

        # 4. Atomic-ish Update
        # Delete existing chunks for this file
        try:
            # Check if doc exists first to avoid error? Chroma delete handles empty fine usually.
            # Using where clause
            print(f"Deleting existing chunks for doc_id={doc_id}")
            # Note: Chroma's delete might require ids or where clause. 
            self.vector_store._collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"Warning during delete: {e}")

        # Add new chunks
        if enriched_chunks:
            self.vector_store.add_documents(enriched_chunks)

        # 5. Update State
        self.state[doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "chunk_count": len(enriched_chunks),
            "indexed_at": timestamp,
            "page_count": len(docs)
        }
        self._save_state()
        
        return {
            "status": "success",
            "chunks": len(enriched_chunks),
            "pages": len(docs)
        }

    def delete_file(self, filename: str) -> Dict:
        """Remove a file from index and disk."""
        doc_id = self._get_doc_id(filename)
        
        # Delete from Vector DB
        try:
            self.vector_store._collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"Error deleting vectors: {e}")

        # Remove from state
        if doc_id in self.state:
            del self.state[doc_id]
            self._save_state()

        # Remove file from disk
        file_path = os.path.join(POLICIES_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return {"status": "success", "message": f"Deleted {filename}"}

    def reset_all(self):
        """Wipe everything and re-index all files in policies dir."""
        # 1. Clear State
        self.state = {}
        self._save_state()

        # 2. Clear Chroma
        # Safest way is to delete the directory and re-init, 
        # but since we have a live instance, we try to delete all.
        try:
             ids = self.vector_store._collection.get()['ids']
             if ids:
                 self.vector_store._collection.delete(ids=ids)
        except Exception as e:
             print(f"Error clearing Chroma: {e}")

        # 3. Re-index all files
        results = []
        files = [f for f in os.listdir(POLICIES_DIR) if f.endswith('.pdf')]
        for f in files:
            try:
                res = self.index_file(f)
                results.append(f"{f}: {res['status']}")
            except Exception as e:
                results.append(f"{f}: Error {str(e)}")
        
        return results

# Singleton instance for simple import
policy_engine = PolicyEngine()
