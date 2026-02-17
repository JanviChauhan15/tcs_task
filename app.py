import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
from agents.graph import get_graph

# Page config
st.set_page_config(page_title="Support Agent System", page_icon="🤖")

st.title("🤖 Enterprise Support Agent")
st.markdown("Ask questions about company policies or customer data.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize graph
if "agent_graph" not in st.session_state:
    st.session_state.agent_graph = get_graph()

# Display chat history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to history
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Inputs for the graph
            inputs = {"messages": st.session_state.messages}
            
            # Run the graph
            # We use invoke here. For streaming, we could use stream()
            result = st.session_state.agent_graph.invoke(inputs)
            
            # The result keys depend on the graph definition. 
            # For create_react_agent, the output state has 'messages'.
            # The last message is the AI response.
            response_messages = result["messages"]
            ai_response = response_messages[-1]
            
            # Display response
            message_placeholder.markdown(ai_response.content)
            
            # Add AI response to history (it's already a message object)
            st.session_state.messages.append(ai_response)
            
        except Exception as e:
            message_placeholder.error(f"An error occurred: {str(e)}")
