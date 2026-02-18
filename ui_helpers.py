import streamlit as st
import sqlite3
import os
import shutil
import streamlit_shadcn_ui as ui
import pandas as pd
import json

DB_PATH = "data/database.sqlite"
POLICIES_DIR = "data/policies"

def get_lucide_script():
    return """
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        // Function to render icons (idempotent)
        function renderIcons() {
            lucide.createIcons();
        }
        
        // Initial render
        renderIcons();
        
        // Observer to re-render when Streamlit updates the DOM
        const observer = new MutationObserver((mutations) => {
            renderIcons();
        });
        
        // Start observing
        document.addEventListener("DOMContentLoaded", () => {
            const container = window.parent.document.body || document.body;
            observer.observe(container, { childList: true, subtree: true });
            renderIcons();
        });
        
        // Fallback interval for robustness
        setInterval(renderIcons, 1000);
    </script>
    <style>
        .lucide { 
            vertical-align: middle; 
            margin-right: 8px; 
            display: inline-block;
            width: 1.25em;    /* Default size adjustment */
            height: 1.25em;
        }
        .lucide-lg { width: 1.5em; height: 1.5em; }
        .lucide-xl { width: 2em; height: 2em; }
        .lucide-xs { width: 0.8em; height: 0.8em; }
    </style>
    """

def lucide_icon(name, size=None, additional_classes=""):
    """
    Renders a Lucide icon using the data attribute.
    Args:
        name: The Lucide icon name (kebab-case, e.g., 'user-check')
        size: Optional size class suffix (lg, xl, xs)
        additional_classes: Extra CSS classes
    """
    size_cls = f"lucide-{size}" if size else ""
    return f'<i data-lucide="{name}" class="lucide {size_cls} {additional_classes}"></i>'

def get_db_status():
    """
    Returns counts of customers and tickets from the database.
    Using sqlite3 directly for speed and reliability.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count Customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        
        # Count Tickets
        # Assuming there is a tickets table, if not catch error
        try:
            cursor.execute("SELECT COUNT(*) FROM tickets")
            ticket_count = cursor.fetchone()[0]
        except:
            ticket_count = 0
            
        conn.close()
        return {"connected": True, "customers": customer_count, "tickets": ticket_count}
    except Exception as e:
        return {"connected": False, "error": str(e)}

def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded PDF to the policies directory.
    """
    if not os.path.exists(POLICIES_DIR):
        os.makedirs(POLICIES_DIR)
        
    file_path = os.path.join(POLICIES_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_indexed_files():
    """
    Lists files in the policies directory.
    """
    if not os.path.exists(POLICIES_DIR):
        return []
    return [f for f in os.listdir(POLICIES_DIR) if f.endswith('.pdf')]

def render_customer_card(data_str):
    """
    Parses a string representation of a list of dicts (from SQL tool)
    and renders a nice Grid layout card.
    """
    try:
        from ast import literal_eval
        data = literal_eval(data_str)
        
        if not isinstance(data, list) or not data:
            st.warning("No data to display.")
            return

        if len(data) == 0:
            st.info("No matching records found in database.")
            return

        # Use efficient grid layout
        st.caption(f"Found {len(data)} customers")
        
        cols = st.columns(3)
        for i, item in enumerate(data[:6]): # Limit to 6
            with cols[i % 3]:
                # Main Card Container
                with st.container(border=True):
                    # Header
                    name = item.get('name', 'Unknown')
                    st.markdown(f"**{name}**")
                    
                    # Badge logic
                    status = item.get('account_status', item.get('status', 'Unknown'))
                    badge_variant = "default" if status == "Active" else "destructive" if status == "Suspended" else "secondary"
                    ui.badges(badge_list=[(status, badge_variant)], key=f"status_{item.get('id')}_{i}")
                    
                    st.divider()
                    
                    # Details
                    email = item.get('email', '-')
                    if email != '-':
                         st.markdown(f"[{email}](mailto:{email})")
                    else:
                        st.caption("No Email")
                        
                    st.caption(f"ID: {item.get('id')}")
                    
        if len(data) > 6:
            st.caption(f"...and {len(data)-6} more.")
            with st.expander("View Raw Data"):
                st.dataframe(pd.DataFrame(data))

    except Exception as e:
        # Fallback if parsing fails
        st.error(f"Render Error: {str(e)}")
        st.code(data_str)

def render_customer_dashboard(data_str):
    """
    Renders a comprehensive customer dashboard from the get_customer_profile tool output.
    Output data structure: {customer, tickets, summary, _meta}
    """
    try:
        from ast import literal_eval
        # The tool might return a raw string dict
        if isinstance(data_str, str):
            data = literal_eval(data_str)
        else:
            data = data_str
            
        if "error" in data:
            st.warning(data["error"])
            return

        customer = data.get("customer", {})
        tickets = data.get("tickets", [])
        summary = data.get("summary", {})
        
        # 1. Profile Card (No large redundant header)
        with st.container(border=True):
            col_avatar, col_info, col_status = st.columns([0.5, 3, 1])
            
            with col_avatar:
                st.markdown(lucide_icon('user-circle', 'xl'), unsafe_allow_html=True)
                
            with col_info:
                st.markdown(f"### {customer.get('name', 'Unknown')}")
                email = customer.get('email', '-')
                if email != '-':
                    st.markdown(f"[{email}](mailto:{email})")
                st.caption(f"Phone: {customer.get('phone', '-')}")
                
            with col_status:
                status = customer.get('account_status', 'Unknown')
                badge_variant = "default" if status == "Active" else "destructive" if status == "Suspended" else "secondary"
                ui.badges(badge_list=[(status, badge_variant)], key="dash_status")
                st.caption(f"ID: {customer.get('id')}")

        st.divider()

        st.divider()

        # 2. Support Summary (Custom Shadcn-style Cards)
        st.subheader("Support Overview")
        
        # Custom CSS for the cards - LIGHT MODE
        st.markdown("""
        <style>
        .shadcn-card {
            background-color: #ffffff;
            border: 1px solid #e4e4e7;
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        .shadcn-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: #71717a;
            font-weight: 500;
        }
        .shadcn-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #09090b;
            line-height: 1;
        }
        .shadcn-desc {
            font-size: 0.8rem;
            color: #71717a;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .trend-badge {
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
        }
        .trend-up { background-color: #dcfce7; color: #166534; }
        .trend-down { background-color: #fee2e2; color: #991b1b; }
        .trend-neutral { background-color: #f4f4f5; color: #71717a; }
        </style>
        """, unsafe_allow_html=True)

        def metric_card_html(title, value, trend=None, desc=None):
            trend_html = ""
            if trend:
                t_val = trend.get("value", "")
                t_type = trend.get("type", "neutral") # up, down, neutral
                trend_html = f'<span class="trend-badge trend-{t_type}">{t_val}</span>'
            
            return f"""
            <div class="shadcn-card">
                <div class="shadcn-header">
                    <span>{title}</span>
                    {trend_html}
                </div>
                <div class="shadcn-value">{value}</div>
                <div class="shadcn-desc">{desc if desc else ""}</div>
            </div>
            """

        m1, m2, m3, m4 = st.columns(4)
        
        # Calculate derived stats for "Trends"
        total = summary.get('total', 0)
        open_t = summary.get('open', 0)
        closed = summary.get('closed', 0)
        high = summary.get('high_priority', 0)
        
        open_pct = round((open_t / total * 100) if total else 0)
        high_pct = round((high / total * 100) if total else 0)

        with m1:
            st.markdown(metric_card_html(
                "Total Tickets", 
                str(total), 
                {"value": "+12.5%", "type": "up"}, 
                "All time volume"
            ), unsafe_allow_html=True)
            
        with m2:
            st.markdown(metric_card_html(
                "Open Tickets", 
                str(open_t), 
                {"value": f"{open_pct}%", "type": "neutral"}, 
                "Active issues"
            ), unsafe_allow_html=True)
            
        with m3:
            st.markdown(metric_card_html(
                "Closed Tickets", 
                str(closed), 
                {"value": "+4%", "type": "up"}, 
                "Resolution rate stable"
            ), unsafe_allow_html=True)
            
        with m4:
             st.markdown(metric_card_html(
                "High Priority", 
                str(high), 
                {"value": f"{high_pct}%", "type": "down" if high_pct > 20 else "neutral"}, 
                "Requires attention"
            ), unsafe_allow_html=True)

        # 3. Recent Activity (Clean Table)
        if tickets:
            st.write("") # Spacer
            st.subheader("Recent Activity")
            
            # Use dataframe for cleaner sortable list or custom columns
            # Custom columns gives us more control over badges
            
            # Header Row
            h1, h2, h3, h4, h5 = st.columns([0.5, 3, 1, 1, 1.5])
            h1.markdown("**ID**")
            h2.markdown("**Subject**")
            h3.markdown("**Priority**")
            h4.markdown("**Status**")
            h5.markdown("**Date**")
            st.divider()
            
            for t in tickets[:5]: 
                c1, c2, c3, c4, c5 = st.columns([0.5, 3, 1, 1, 1.5])
                c1.caption(f"#{t.get('id')}")
                c2.write(t.get('subject'))
                
                # Priority
                prio = t.get('priority', 'Low')
                prio_color = "red" if prio == "High" else "orange" if prio == "Medium" else "gray"
                c3.markdown(f":{prio_color}[{prio}]")
                
                # Status Badge
                s = t.get('status', 'Open')
                s_variant = "outline" if s == "Open" else "secondary"
                with c4:
                    ui.badges(badge_list=[(s, s_variant)], key=f"t_{t.get('id')}")
                    
                c5.caption(t.get('created_at'))
        else:
            st.info("No ticket history.")
                
    except Exception as e:
        st.error(f"Dashboard Render Error: {e}")
        st.code(str(data_str))
