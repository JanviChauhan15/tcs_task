# 🤖 Janvi AI - Multi-Agent Customer Support System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-green.svg)](https://www.langchain.com)
[![Groq](https://img.shields.io/badge/Groq-Llama3-orange.svg)](https://groq.com)

##  Project Overview

**Janvi AI** is a production-grade, multi-agent customer support system designed to autonomously handle complex user queries by routing them to specialized tools. It solves the problem of static chatbots by combining **Structured Data Access (SQL)** with **Unstructured Knowledge Retrieval (RAG)** in a unified interface.

### Key Capabilities:
- **Policy Answers**: Retrieves accurate answers from PDF policy documents (e.g., "What is the refund policy?").
- **Customer Data**: Queries a SQL database to fetch real-time customer profiles, ticket status, and history.
- **Intelligent Routing**: A Supervisor Agent (powered by LangGraph) decides whether to use SQL, RAG, or both.
- **Evidence-Based**: All policy answers include strict inline citations to the source document and page number.

---

## Architecture

The system follows a **Multi-Agent Architecture** using **LangGraph**:

```mermaid
graph TD
    User[User Query] --> Graph[Supervisor Agent (Groq Llama-3)]
    Graph -->|Policy Q| RAG[RAG Agent]
    Graph -->|Data Q| SQL[SQL Agent]
    RAG -->|Context| Graph
    SQL -->|Rows| Graph
    Graph -->|Final Answer| UI[Streamlit UI]
```

1.  **Streamlit UI**: The frontend interface for chat and specific admin actions (uploading docs, resetting DB).
2.  **Supervisor Agent**: The brain. It analyzes the intent and routes the query.
3.  **RAG Agent**:
    *   **Vector DB**: ChromaDB stores semantic chunks of PDF policies.
    *   **Embeddings**: `all-MiniLM-L6-v2` (HuggingFace) converts text to vectors.
4.  **SQL Agent**:
    *   **Database**: SQLite (`data/database.sqlite`) stores `customers` and `tickets`.
    *   **Safety**: Read-only access to prevent data modification by the LLM.

---

## 🛠️ Tech Stack

-   **LLM**: Groq (`llama-3.1-8b-instant`) for ultra-fast inference.
-   **Orchestration**: LangChain & LangGraph.
-   **Frontend**: Streamlit + Shadcn UI (for modern components).
-   **Database**: SQLite (Relational), ChromaDB (Vector).
-   **Embeddings**: HuggingFace (`sentence-transformers`).
-   **Language**: Python 3.10+.

---

## � Installation & Setup

Follow these steps to get the project running on your local machine.

### 1. Get the Project
First, you need to download the code from GitHub. Open your terminal and run:

```bash
git clone https://github.com/JanviChauhan15/tcs_task.git
cd tcs_task
```

### 2. Set Up Your Environment
It is best practice to use a virtual environment to keep dependencies organized.

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
Install all the required Python libraries content in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
**No Setup Required:** A valid API key is provided for testing purposes. You do not need to create a Groq account.

1.  Create a file named `.env` in the project folder.
2.  Paste the **API Key provided with this project**:

```env
GROQ_API_KEY=gsk_... [Key Removed for Security - Please Request from Author]
```

### 5. Initialize the Database
Before running the app, we need to create the database and add some dummy data to test with.

```bash
python scripts/init_db.py
```

---

## ▶️ Usage Guide

### Run the Application
To start the interface, run:

```bash
streamlit run app.py
```
A new tab will open in your web browser at `http://localhost:8501`.

### How to Use
1.  **Chat**: Type your questions in the input box.
2.  **Upload Policies**: Use the sidebar to upload PDF documents (e.g., "Refund Policy"). The AI will instantly read and learn them.
3.  **Reset**: If things get messy, click "Reset Database" in the sidebar to restore the default data.

### Example Questions to Ask
Try these to see the agent in action:

*   **Data Questions**: "List all suspended customers."
*   **Policy Questions**: "What is the refund policy?"
*   **Profile Lookup**: "Show me the profile for Ema Patel."
*   **Complex**: "Check Ema Patel's status and tell me if she is eligible for a refund."

---

## 📂 Project Structure

Here is how the code is organized:

```
├── agents/
│   ├── graph.py          # The "Brain" (Supervisor) that decides what to do
│   ├── rag_agent.py      # The "Librarian" -> Reads PDFs and answers policy questions
│   ├── sql_agent.py      # The "Data Analyst" -> Queries the database
│   └── utils_sql.py      # Helper tools for safe SQL queries
├── app.py                # The main website (Frontend UI)
├── data/
│   ├── chroma_db/        # The AI's long-term memory (Vector DB)
│   ├── policies/         # Folder where your uploaded PDFs go
│   └── database.sqlite   # The customer database file
├── scripts/
│   ├── init_db.py        # Script to create dummy data
│   └── ingest_docs.py    # Script to process documents
├── services/
│   └── policy_engine.py  # Logic for handling file uploads/indexing
├── requirements.txt      # List of all Python libraries used
└── .env                  # Your secret API keys (hidden)
```
