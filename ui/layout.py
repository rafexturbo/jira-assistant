import streamlit as st
from typing import Dict

def setup_layout() -> None:
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Optimal UI</div>', unsafe_allow_html=True)
        menu_items = {
            "Transcript": "📊",
            "Tasks": "📝",
            "Settings": "⚙️"
        }
        
        current_page = st.session_state.get('current_page', 'Tasks')
        
        for page, icon in menu_items.items():
            if st.button(f"{icon} {page}", key=f"menu_{page}", 
                        help=f"Go to {page}",
                        use_container_width=True):
                if page == "Settings":
                    st.session_state.show_config = True
                else:
                    st.session_state.show_config = False
                st.session_state.current_page = page
                st.rerun()

    # Add title
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">AI PRODUCT OWNER</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Main content
    st.markdown('<div class="main-content">', unsafe_allow_html=True) 