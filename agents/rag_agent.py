from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = "data/chroma_db"

from langchain_core.tools import tool

@tool
def query_policies(query: str) -> str:
    """
    Search for information about company policies, refunds, shipping, and other document-related questions.
    Returns the relevant text chunks and their source documents.
    """
    try:
        # Re-initialize internally to ensure we get fresh state if needed
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
        # Retrieve top 4 results (increased from 3 for better coverage)
        results = vectorstore.similarity_search(query, k=4)
        
        debug_info = {
            "query": query,
            "retrieved_count": len(results),
            "top_source": results[0].metadata.get("source", "N/A") if results else "None"
        }

        if not results:
             return f"No relevant policy information found in indexed documents about '{query}'. (Debug: 0 chunks found)"
        
        # Format output for the LLM
        formatted_results = []
        source_list = []
        for i, doc in enumerate(results):
            source = doc.metadata.get("doc_name", os.path.basename(doc.metadata.get("source", "Unknown")))
            page = doc.metadata.get("page", "N/A")
            content = doc.page_content.replace("\n", " ")
            formatted_results.append(f"Source {i+1}: {source} (Page {page})\nContent: {content}\n")
            source_list.append(f"{source} (p. {page})")
            
        context_str = "\n".join(formatted_results)
        
        # We return the raw context to the LLM, but we append a strict instruction
        # This is because the tool output goes back to the graph/LLM to generate the final answer.
        return f"""
Context:
{context_str}

Debug: {str(debug_info)}
Sources: {", ".join(list(set(source_list)))}
"""
        
    except Exception as e:
        return f"Error querying policies: {str(e)}"
