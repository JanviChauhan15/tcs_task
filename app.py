import streamlit as st
import os
import time
import streamlit_shadcn_ui as ui
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from agents.graph import get_graph
from ui_helpers import get_db_status, save_uploaded_file, list_indexed_files, get_lucide_script, lucide_icon

# Page config
st.set_page_config(page_title="Janvi Support", page_icon="⚛️", layout="wide", initial_sidebar_state="expanded")

# Inject Lucide Icons & Custom CSS
st.markdown(get_lucide_script(), unsafe_allow_html=True)
st.markdown("""
<style>
    /* Hide Streamlit default menu but keep sidebar accessible */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Center the main block for chat */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Hero Section Styling */
    .hero-container {
        text-align: center;
        padding: 4rem 1rem;
        max-width: 700px;
        margin: 0 auto;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #111827;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* CUSTOM CHAT STYLING */
    /* User Message */
    .user-message {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 1rem 1.25rem;
        border-radius: 1.5rem 1.5rem 0 1.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e5e7eb;
        display: inline-block;
        /* float: right; This breaks standard flow usually, but we'll try alignment */
    }
    
    /* Bot Message */
    .bot-message {
        background-color: #ffffff;
        color: #111827;
        padding: 1rem 1.25rem;
        border-radius: 1.5rem 1.5rem 1.5rem 0;
        margin-bottom: 0.5rem;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #6366f1; /* Indigo Accent */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Remove default streamlit container padding for cleaner look if needed */
    /* .stChatMessage { padding: 0.5rem; } */
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_graph" not in st.session_state:
    st.session_state.agent_graph = get_graph()

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# --- SIDEBAR: ADMIN & INFO ---
with st.sidebar:
    st.markdown(f"### {lucide_icon('atom', 'lg')} Janvi Support", unsafe_allow_html=True)
    st.divider()
    
    # Primary Action
    if ui.button("New Conversation", key="new_chat", className="w-full", variant="primary"):
        st.session_state.messages = []
        st.rerun()

    st.write("") # Spacer

    # Admin Control Panel (Collapsible to keep it clean)
    with st.expander("Admin Controls", expanded=True):
        st.caption("System Operations")
        
        # 1. DB Stats
        db_status = get_db_status()
        c1, c2 = st.columns(2)
        c1.metric("Customers", db_status.get("customers", 0))
        c2.metric("Tickets", db_status.get("tickets", 0))
        
        # 2. Re-seed
        if st.button("Reset Database", key="reseed_btn", use_container_width=True):
             os.system("python scripts/init_db.py") 
             st.toast("Database reset complete!", icon="✅")
             time.sleep(1)
             st.rerun()

    with st.expander("Knowledge Base", expanded=False):
        # 1. Upload
        uploaded_file = st.file_uploader("Upload Policy (PDF)", type="pdf")
        if uploaded_file:
            # Generate a unique ID for this upload instance
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            
            if file_id not in st.session_state.processed_files:
                save_path = save_uploaded_file(uploaded_file)
                st.toast(f"Uploaded: {uploaded_file.name}")
                
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    from services.policy_engine import policy_engine
                    res = policy_engine.index_file(uploaded_file.name)
                    st.success(f"Indexed {res.get('chunks')} chunks!")
                    
                # Mark as processed
                st.session_state.processed_files.add(file_id)
                time.sleep(1)
                st.rerun()

        st.divider()

        # 2. Global Actions
        if st.button("Re-index ALL Documents", key="reindex_all_btn", use_container_width=True, type="secondary"):
            with st.spinner("Resetting & Indexing All..."):
                from services.policy_engine import policy_engine
                res = policy_engine.reset_all()
            st.success("Re-indexing Complete!")
            time.sleep(1)
            st.rerun()

        st.divider()
        st.caption("Indexed Documents:")
        
        # 3. List & Item Actions
        from services.policy_engine import policy_engine
        try:
            docs = policy_engine.get_indexed_files()
        except:
            docs = []

        if not docs:
            st.caption("No documents in index.")
        else:
            for doc in docs:
                filename = doc.get('filename')
                doc_id = doc.get('doc_id')
                
                # Card for each doc
                with st.container(border=True):
                    st.markdown(f"**{lucide_icon('file-text', 'xs')} {filename}**", unsafe_allow_html=True)
                    st.caption(f"Chunks: {doc.get('chunk_count')} | Pages: {doc.get('page_count', '?')}")
                    
                    # Row of mini buttons
                    b1, b2 = st.columns(2)
                    if b1.button("Re-index", key=f"re_{doc_id}", use_container_width=True):
                        with st.spinner("Re-indexing..."):
                            policy_engine.index_file(filename)
                        st.toast("Updated!", icon="🔄")
                        time.sleep(0.5)
                        st.rerun()
                        
                    if b2.button("Remove", key=f"del_{doc_id}", use_container_width=True):
                        with st.spinner("Deleting..."):
                            policy_engine.delete_file(filename)
                        st.toast("Deleted!", icon="🗑️")
                        time.sleep(0.5)
                        st.rerun()

    st.divider()
    
    # System Status Footer
    st.markdown("**System Status**")
    # FIX: Removed the 3rd argument 'fill' which caused the crash
    st.markdown(f"{lucide_icon('circle', 'xs', 'fill-current text-green-500')} Online", unsafe_allow_html=True)
    st.caption("v1.0.1")

# --- MAIN VIEW: CHAT ---

# Empty State / Hero Section
if not st.session_state.messages:
    # Use simple HTML for Hero
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">{lucide_icon('sparkles', 'xl')} Janvi AI</div>
        <div class="hero-subtitle">Ask me anything about policies, customers, or tickets.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggested Queries (Centered Pills)
    _, mid, _ = st.columns([1, 4, 1])
    with mid:
        cols = st.columns(3)
        if cols[0].button("List suspended customers", use_container_width=True):
            st.session_state.messages.append(HumanMessage(content="List suspended customers"))
            st.rerun()
        if cols[1].button("Refund Policy", use_container_width=True):
             st.session_state.messages.append(HumanMessage(content="What is the refund policy?"))
             st.rerun()
        if cols[2].button("Ema Patel Profile", use_container_width=True):
             st.session_state.messages.append(HumanMessage(content="Show me customer profile for Ema Patel"))
             st.rerun()

# Chat History
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
         with st.chat_message("user"):
            # Wrap in custom container
            st.markdown(f'<div class="user-message">{message.content}</div>', unsafe_allow_html=True)
    elif isinstance(message, AIMessage):
        if message.content:
            with st.chat_message("assistant"):
                # Wrap in custom container
                st.markdown(f'<div class="bot-message">{message.content}</div>', unsafe_allow_html=True)

# Input Area
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.rerun()

# Processing Logic (Hidden/Auto-run after rerun)
if st.session_state.messages and isinstance(st.session_state.messages[-1], HumanMessage):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                # Inputs for the graph
                system_prompt = SystemMessage(content="You are a helpful customer support supervisor. When a tool returns an answer, you MUST repeat that answer to the user clearly.")
                messages_in = [system_prompt] + st.session_state.messages
                
                # Check initial length to identify new messages
                initial_len = len(st.session_state.messages)
                
                # Run graph
                result = st.session_state.agent_graph.invoke({"messages": messages_in}, config={"recursion_limit": 50})
                full_history = result["messages"]
                
                # Update session state with full history (excluding system)
                st.session_state.messages = [m for m in full_history if not isinstance(m, SystemMessage)]
                
                # Output Handling
                final_msg = st.session_state.messages[-1]
                content = final_msg.content
                
                # Detect Tool Data for Cards (Only in NEW messages)
                tool_data = None
                
                # We only want to look at messages that were added in this turn
                # The session_state.messages list has grown. 
                # new_messages = st.session_state.messages[initial_len:]
                
                # Scan BACKWARDS through the history, stopping at the point where we started this turn
                # This ensures we don't pick up tool outputs from previous turns.
                for i in range(len(st.session_state.messages)-1, initial_len-1, -1):
                     msg = st.session_state.messages[i]
                     if isinstance(msg, ToolMessage) and msg.name == "query_sql_db":
                         tool_data = msg.content
                         break
                
                # Render Answer
                if not content:
                     content = "⚠️ No response generated. Please check Inspect Trace."
                
                # Wrap the final content in the bot-message style
                message_placeholder.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)
                
                # --- SOURCE CITATION DISPLAY ---
                # Attempt to extract sources from the ToolMessage content if available
                sources_found = []
                retrieval_debug = "No retrieval performed."
                
                if tool_data and "METADATA_SOURCES:" in tool_data:
                    try:
                        # Simple parsing from the string we injected in rag_agent.py
                        parts = tool_data.split("METADATA_SOURCES:")[1].split("DEBUG_INFO:")[0].strip()
                        if parts:
                             sources_found = [s.strip() for s in parts.split(",")]
                             
                        # Extract Debug Info
                        if "DEBUG_INFO:" in tool_data:
                             retrieval_debug = tool_data.split("DEBUG_INFO:")[1].strip()
                    except:
                        pass
                
                # Render Sources cleanly below the bubble
                if sources_found:
                    with st.container():
                        st.caption(f"📚 **Sources:** {', '.join(sources_found)}")
                
                # --- TRACE & DEBUG ---
                with st.expander("Inspect Trace & Debug"):
                    st.caption(f"**Retrieval Stats:** {retrieval_debug}")
                    st.caption("Agent execution trace:")
                    if tool_data:
                        st.code(tool_data, language="text")
                    else:
                        st.info("No tool calls in this turn.")
                    
            except Exception as e:
                message_placeholder.error(f"Error: {e}")
                # Remove the failed message to prevent stuck state
                st.session_state.messages.pop()
