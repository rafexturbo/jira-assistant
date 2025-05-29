import streamlit as st
import openai
import json
from typing import Dict, Any
import requests

from config.settings import PAGE_CONFIG, DEVELOPER_ACCOUNT_IDS
from ui.styles import CUSTOM_CSS
from ui.layout import setup_layout
from ui.components import show_task_cards, show_configuration
from services.task_processor import parse_tasks_with_assignees
from services.pdf_service import json_to_pdf, format_tasks_from_transcript
from services.jira_service import inject_tasks_to_jira
from services.priority_utils import map_number_to_id

# Set page config
st.set_page_config(**PAGE_CONFIG)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Setup layout
setup_layout()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "accepted_tasks" not in st.session_state:
    st.session_state.accepted_tasks = []
if "parsed_tasks" not in st.session_state:
    st.session_state.parsed_tasks = []
if "config" not in st.session_state:
    st.session_state.config = {
        "openai_key": None,
        "epic_mapping": {},
        "is_configured": False
    }
if "show_config" not in st.session_state:
    st.session_state.show_config = not st.session_state.config["is_configured"]

# Add navigation to Push to Jira screen
if "show_push_to_jira" not in st.session_state:
    st.session_state.show_push_to_jira = False

# Handle navigation for Transcript page
if st.session_state.get('current_page') == 'Transcript':
    st.title('Transcript')
    st.markdown('Choose an action:')
    if 'show_transcript_uploader' not in st.session_state:
        st.session_state.show_transcript_uploader = False
    if st.button('Extract Tasks from Review'):
        st.markdown('''
**VSAT Blocakge**

**Ruan:**
• Develop V1 of the agent's final classification logic combining inputs from SNR, image classification, hexagon data (if available), and docking schedule (if available).
• Integrate hexagon data into the agent's controller.

**Llum:**
• Decide with Moha the features we want to try next (suggestions: vessel speed, antenna direction,  satellite pointing direction and other like Tx)
• Create an new version of the dataset with these new features

**Mohamed:**
• Create an new dataset for Nazario with 200 tickets from Lllum dataset. Use samples from Resolution Summary that explicitly mentions blockage, and also other cause codes.  
• Cluster analysis in the dataset to check if features are aligned with labels

**Nazario:**
• Review and validate the first batch of 50 blockage samples.
• Review and validate the second batch of 50 blockage samples.

**Chatbot:**

**David:**
• Implement ticket Similarity into Freshdesk.
''')
        st.stop()
    if st.button('Extract Tasks from Daily'):
        st.info('Extract Tasks from Daily clicked (placeholder)')
        st.stop()
    if st.button('Insert Meeting Transcript') or st.session_state.show_transcript_uploader:
        st.session_state.show_transcript_uploader = True
        uploaded_file = st.file_uploader("Upload Meeting Transcript (PDF)", type=["pdf"])
        if uploaded_file is not None:
            pdf_bytes = uploaded_file.read()
            with st.spinner("Extracting tasks from transcript..."):
                formatted_output = format_tasks_from_transcript(pdf_bytes, api_key=st.session_state.config.get("openai_key"))
            st.markdown("### Extracted Action Items")
            st.code(formatted_output)
        st.stop()

# Configuration Screen
if st.session_state.show_config or not st.session_state.config.get("is_configured"):
    show_configuration()
    st.stop()

# Set OpenAI key from config
openai.api_key = st.session_state.config.get("openai_key")

# Main Interface
st.markdown("#### Enter a list of functionalities (one per line):")
user_input = st.text_area("", height=120, key="functionality_input")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    enhance_clicked = st.button("Enhance Tasks")
with col2:
    reset_clicked = st.button("Reset Chat")
with col3:
    if st.button("🚀 Push to Jira"):
        st.session_state.show_push_to_jira = True
        st.rerun()

if reset_clicked:
    st.session_state.messages = []
    st.session_state.accepted_tasks = []
    st.session_state.parsed_tasks = []
    st.rerun()

# Process tasks when enhance button is clicked
if enhance_clicked and user_input.strip():
    try:
        st.session_state.parsed_tasks = parse_tasks_with_assignees(user_input.strip())
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()
    except Exception as e:
        st.error(f"Error processing tasks: {str(e)}")

# Show chat history and task cards
ai_msg_idx = 0
for msg_idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:**\n```\n{msg['content']}\n```", unsafe_allow_html=True)
    else:
        # Extract tasks from the response
        tasks = []
        content = msg["content"]
        
        # First try to find tasks in the format "### Task: ..."
        task_parts = content.split("### Task:")
        if len(task_parts) > 1:
            tasks = [part.strip() for part in task_parts[1:]]  # Skip the first part (before first task)
        
        if tasks:
            show_task_cards(tasks, msg_idx, msg)
        else:
            st.error("Could not parse tasks from the response")
            st.code(content)  # Show the raw response for debugging
        ai_msg_idx += 1

# Show accepted tasks summary
if st.session_state.accepted_tasks:
    st.markdown("---")
    st.markdown("### Accepted Tasks:")
    for t in st.session_state.accepted_tasks:
        st.markdown(f"**{t['task_name']}**\n\n{t['description']}\n\nAssignee: {t['assignee']}\n- " + "\n- ".join(t['acceptance_criteria']))

    # Export to JSON and PDF
    st.markdown("---")
    if st.button("Format to JSON & Download PDF"):
        jira_tasks = []
        has_errors = False
        error_messages = []

        for task in st.session_state.accepted_tasks:
            jira_task = {
                "fields": {
                    "project": {"key": "AI"},
                    "issuetype": {"name": task.get("issuetype", "Story")},
                    "summary": task["task_name"][:254],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {"type": "paragraph", "content": [
                                {"type": "text", "text": task["description"]}
                            ]},
                            {"type": "paragraph", "content": [
                                {"type": "text", "text": "Acceptance Criteria:"}
                            ]},
                            {"type": "bulletList", "content": [
                                {"type": "listItem", "content": [
                                    {"type": "paragraph", "content": [
                                        {"type": "text", "text": crit}
                                    ]}
                                ]} for crit in task["acceptance_criteria"]
                            ]}
                        ]
                    },
                    "labels": ["ai-generated"],
                    "parent": {"key": task["epic_key"]},
                    "priority": {"id": map_number_to_id(task.get("priority_num", 3))}
                }
            }

            # Add assignee if specified
            if task["assignee"]:
                account_id = DEVELOPER_ACCOUNT_IDS.get(task["assignee"])
                if account_id:
                    jira_task["fields"]["assignee"] = {"id": account_id}
                else:
                    has_errors = True
                    error_messages.append(f"Error: Could not find account ID for assignee '{task['assignee']}'")
                    continue

            jira_tasks.append(jira_task)

        if has_errors:
            st.error("Failed to generate JSON due to the following errors:")
            for error in error_messages:
                st.error(error)
        else:
            jira_json = {"issueUpdates": jira_tasks}
            try:
                pdf_bytes = json_to_pdf(jira_json)
                st.success("Jira JSON formatted and PDF generated!")
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name="jira_tasks.pdf",
                    mime="application/pdf"
                )
                with st.expander("View JSON"):
                    st.json(jira_json)
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
else:
    st.info("No tasks have been accepted yet. Accept tasks to enable export.")

# Main accepted tasks and export screen
if not st.session_state.show_push_to_jira:
    # ... existing code for accepted tasks and export ...
    # (leave as is)
    pass
else:
    st.title("Push Tasks to Jira Cloud")
    st.markdown("Review your tasks below and push them directly to Jira.")

    # Show tasks summary
    for i, t in enumerate(st.session_state.accepted_tasks):
        st.markdown(f"**{i+1}. {t['task_name']}**\nAssignee: {t['assignee']}\nEpic: {t['epic_key']}")

    # Collect Jira credentials if not already in config
    config = st.session_state.config
    jira_url = st.text_input("Jira Site URL", value=config.get("jira_url", ""))
    email = st.text_input("Atlassian Email", value=config.get("jira_email", ""))
    api_token = st.text_input("API Token", value=config.get("jira_api_token", ""), type="password")

    # Save credentials to config
    if st.button("Save Jira Credentials"):
        config["jira_url"] = jira_url
        config["jira_email"] = email
        config["jira_api_token"] = api_token
        st.success("Jira credentials saved!")

    # Prepare JSON
    jira_tasks = []
    for task in st.session_state.accepted_tasks:
        jira_task = {
            "fields": {
                "project": {"key": "AI"},
                "issuetype": {"name": task.get("issuetype", "Story")},
                "summary": task["task_name"][:254],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": task["description"]}
                        ]},
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": "Acceptance Criteria:"}
                        ]},
                        {"type": "bulletList", "content": [
                            {"type": "listItem", "content": [
                                {"type": "paragraph", "content": [
                                    {"type": "text", "text": crit}
                                ]}
                            ]} for crit in task["acceptance_criteria"]
                        ]}
                    ]
                },
                "labels": ["ai-generated"],
                "parent": {"key": task["epic_key"]},
                "priority": {"id": map_number_to_id(task.get("priority_num", 3))}
            }
        }
        if task["assignee"]:
            account_id = DEVELOPER_ACCOUNT_IDS.get(task["assignee"])
            if account_id:
                jira_task["fields"]["assignee"] = {"id": account_id}
        jira_tasks.append(jira_task)
    jira_json = {"issueUpdates": jira_tasks}

    # Push to Jira
    if st.button("Push to Jira Cloud"):
        if not (jira_url and email and api_token):
            st.error("Please provide all Jira credentials.")
        elif not jira_tasks:
            st.error("No tasks to push.")
        else:
            with st.spinner("Pushing tasks to Jira..."):
                try:
                    # Directly call Jira Cloud API using helper
                    success, result = inject_tasks_to_jira(jira_url, email, api_token, jira_json)
                    if success:
                        st.success("Tasks pushed to Jira successfully!")
                    else:
                        st.error(f"Failed to push tasks: {result}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.button("⬅️ Back"):
        st.session_state.show_push_to_jira = False
        st.rerun() 