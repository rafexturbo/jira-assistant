"""
CSS styles for the JIRA Task Assistant UI.
"""

CUSTOM_CSS = """
    <style>
    .main {
        background-color: #f5f5f7;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    /* Remove default Streamlit spacing */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
    }
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Adjust header margins */
    .stMarkdown h1 {
        margin: 0.5rem 0 !important;
        padding: 0 !important;
    }
    .stMarkdown h2 {
        margin: 1rem 0 !important;
        padding: 0 !important;
    }
    .stSidebar {
        background-color: white;
        padding: 2rem 1rem;
    }
    .sidebar-menu {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }
    .sidebar-menu li {
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .sidebar-menu li:hover {
        background-color: #f0f0f4;
    }
    .sidebar-menu li.active {
        background-color: #6b46c1;
        color: white;
    }
    .stTextArea textarea {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 12px;
        font-size: 16px;
    }
    .stButton button {
        background-color: #6b46c1;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #553c9a;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        padding: 1.5rem !important;
    }
    div.stMarkdown {
        padding: 1rem 0;
    }
    .main-title {
        color: #6b46c1;
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin: 0.5rem 0 1rem 0 !important;
        letter-spacing: 1px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .title-container {
        padding-left: 1.5rem;
        margin-top: 0;
    }
    .configuration-section {
        margin-top: 0.5rem;
    }
    .main-content {
        padding-top: 1.5rem;
    }
    .stSelectbox {
        background-color: white;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 8px 12px;
    }
    .success-message {
        padding: 1rem;
        background-color: #dcf8c6;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #ffdede;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .task-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E1E1E;
        margin-bottom: 1rem;
    }
    .config-section {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    /* Hide the top buttons and title */
    [data-testid="stToolbar"] {
        display: none;
    }
    </style>
""" 