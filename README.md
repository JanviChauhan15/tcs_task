# Generative AI Multi-Agent System

This project implements a Multi-Agent System using LangChain, LangGraph, and OpenAI to handle queries for both structured customer data (SQL) and unstructured policy documents (RAG).

## Architecture

The system consists of a Supervisor/Router agent that delegates queries to specialized tools:
1.  **CustomerDB Tool (SQL Agent)**: Queries a SQLite database containing customer profiles and ticket history.
2.  **PolicyDocs Tool (RAG Agent)**: Queries a ChromaDB vector store containing company policy PDF documents.

The UI is built with Streamlit.

## Setup Instructions

### Prerequisites
- Python 3.9+
- OpenAI API Key

### Installation

1.  Clone the repository (if applicable) or navigate to the project directory.
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`

### Initialization

1.  Initialize the database and dummy data:
    ```bash
    python scripts/init_db.py
    python scripts/create_dummy_pdf.py
    ```
2.  Ingest documents into the vector database:
    ```bash
    python scripts/ingest_docs.py
    ```

### Running the Application

Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage Examples

- **Policy Query**: "What is the refund policy?"
- **Customer Query**: "Show me the last ticket for Ema Stone."
- **Customer Query**: "Who has a Platinum membership?"
- **Policy Query**: "Are gift cards refundable?"

## Files Structure

- `agents/`: Contains agent implementations (SQL, RAG, Supervisor).
- `data/`: Stores SQLite DB and PDF documents.
- `scripts/`: Helper scripts for setup.
- `app.py`: Main Streamlit application.

## Troubleshooting

### "429 Quota Exceeded" Error
If you see an error like `ResourceExhausted: 429... limit: 0`, it means your Google Cloud project does not have the Free Tier enabled or billing set up correctly.
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Ensure you have added a billing account (to activate the free $300 credit) or selected the correct "Free Tier" options.
3.  You will **not** be charged for this project (it stays well within the free limits), but Google requires the setup to unlock the quota.

### "Command not found: streamlit"
If you see this error, make sure your virtual environment is active:
```bash
source venv/bin/activate
```

