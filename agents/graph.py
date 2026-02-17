import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Union, Literal
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
import operator

# Import our agents
from agents.sql_agent import get_sql_agent
from agents.rag_agent import get_rag_chain

load_dotenv()

# Define tools for the supervisor to call
def query_sql_db(query: str):
    """
    Useful for querying customer data, tickets, and structured information from the database.
    Input should be a natural language question.
    """
    agent = get_sql_agent()
    result = agent.invoke({"input": query})
    return result['output']

def query_policies(query: str):
    """
    Useful for querying company policies, refund rules, and other document-based information.
    Input should be a natural language question.
    """
    chain = get_rag_chain()
    result = chain.invoke({"input": query})
    return result['answer']

tools = [
    Tool(
        name="CustomerDB",
        func=query_sql_db,
        description="Useful for querying customer data and support tickets."
    ),
    Tool(
        name="PolicyDocs",
        func=query_policies,
        description="Useful for querying company policies and documents."
    )
]

# Using a simpler ReAct style agent since we want a supervisor to route
# Or we can just use the tools directly with an agent.
# Let's create a graph with a single node that calls the LLM with tools bound, 
# and then executes the tool.

from langgraph.prebuilt import create_react_agent

def get_graph():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    graph = create_react_agent(llm, tools=tools)
    return graph
