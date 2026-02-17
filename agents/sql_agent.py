from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

def get_sql_agent():
    db = SQLDatabase.from_uri("sqlite:///data/database.sqlite")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Create the SQL agent
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )
    
    return agent_executor
