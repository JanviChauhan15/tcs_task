import os
from typing import TypedDict, List, Any, Dict, Annotated
import operator
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our tools
from agents.utils_sql import query_sql_db, get_customer_profile
from agents.rag_agent import query_policies

load_dotenv()

# 1) Groq LLM (Pure Groq)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# 2) Tools
# query_policies is already a @tool, so we don't need to call it like a factory
tools = [query_sql_db, get_customer_profile, query_policies]

# 3) Bind tools to Groq model
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def assistant_node(state: AgentState) -> Dict:
    """
    The model decides whether to answer directly or call tools.
    """
    # Simply invoke the model with tools bound
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

def should_call_tools(state: AgentState) -> str:
    """
    If the model returned tool_calls, route to tool node. 
    Prevents infinite loops by checking if the tool was already called.
    """
    last_message = state["messages"][-1]
    
    # 1. No tool calls? End.
    if not (hasattr(last_message, "tool_calls") and last_message.tool_calls):
        return "end"
        
    # 2. Check for redundant tool calls (Loop Prevention)
    # We look at previous ToolMessages to see if we already executed this tool.
    proposed_tools = [tc["name"] for tc in last_message.tool_calls]
    
    messages = state["messages"]
    # Scan backwards
    for msg in reversed(messages[:-1]): 
        if isinstance(msg, SystemMessage):
            continue
        if hasattr(msg, "name") and msg.name in proposed_tools:
            # We found a previous execution of this tool.
            # Stop the loop. We assume the agent is confused or trying to retry endlessly.
            # We return "end" so the agent just stops with whatever response it has.
            return "end"
            
    return "tools"

def get_graph():
    graph = StateGraph(AgentState)
    graph.add_node("assistant", assistant_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("assistant")
    
    # Conditional routing
    graph.add_conditional_edges(
        "assistant", 
        should_call_tools, 
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Loop back from tools to assistant
    graph.add_edge("tools", "assistant")

    return graph.compile()
