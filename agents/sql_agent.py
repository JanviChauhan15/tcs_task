from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import os

def get_sql_agent():
    db = SQLDatabase.from_uri("sqlite:///data/database.sqlite")
    # Using ChatOpenAI with Groq Endpoint
    llm = ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    
    # Create the SQL agent
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": True},
        prefix="You are an agent designed to interact with a SQLite database. Do not assume table names or column names. Always check the schema using sql_db_schema before running a query."
    )
    
    return agent_executor
