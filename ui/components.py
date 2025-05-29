import streamlit as st
from typing import List, Dict, Any

from config.settings import DEVELOPERS, DEVELOPER_ACCOUNT_IDS

def show_task_cards(tasks: List[Dict[str, Any]], msg_idx: int, msg: Dict[str, Any]) -> None:
    for i, task_block in enumerate(tasks):
        lines = task_block.strip().split('\n')
        task_title = lines[0].strip()  # First line is the title
        # Find description and criteria
        description = ""
        criteria = []
        in_criteria = False
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if "**Description:**" in line:
                description = line.replace("**Description:**", "").strip()
            elif "**Acceptance Criteria:**" in line:
                in_criteria = True
            elif in_criteria and line.startswith("-"):
                criteria.append(line.strip().lstrip("- "))
        # Get task-specific data from parsed tasks
        assignee = None
        epic_name = None
        epic_key = None
        if len(st.session_state.parsed_tasks) > i:
            task_data = st.session_state.parsed_tasks[i]
            assignee = task_data.get("assignee")
            epic_name = task_data.get("epic_name")
            epic_key = task_data.get("epic_key")
        with st.expander(f"Task: {task_title}", expanded=False):
            desc_key = f"desc_{msg_idx}_{i}"
            crit_key = f"crit_{msg_idx}_{i}"
            accept_key = f"accept_{msg_idx}_{i}"
            assignee_key = f"assignee_{msg_idx}_{i}"
            epic_key_widget = f"epic_{msg_idx}_{i}"
            priority_key = f"priority_{msg_idx}_{i}"
            issuetype_key = f"issuetype_{msg_idx}_{i}"
            # 2x2 grid for Epic, Assignee, Priority, Issue Type
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Epic**")
                epic_options = [f"{name} ({key})" for name, key in st.session_state.config["epic_mapping"].items()]
                default_index = 0
                if epic_name and epic_key:
                    try:
                        default_index = epic_options.index(f"{epic_name} ({epic_key})")
                    except ValueError:
                        pass
                selected_epic = st.selectbox(
                    "Epic",
                    options=epic_options,
                    key=epic_key_widget,
                    index=default_index
                )
                # Priority selectbox (1-5)
                priority_num = None
                if len(st.session_state.parsed_tasks) > i:
                    priority_num = st.session_state.parsed_tasks[i].get("priority_num", 3)
                priority = st.selectbox(
                    "Priority (1-highest, 5-lowest)",
                    [1, 2, 3, 4, 5],
                    index=(priority_num or 3) - 1,
                    key=priority_key
                )
                if len(st.session_state.parsed_tasks) > i:
                    st.session_state.parsed_tasks[i]["priority_num"] = priority
            with col2:
                st.markdown("**Assignee**")
                if assignee:
                    st.text_input("Assignee", value=assignee, key=assignee_key, disabled=True)
                    final_assignee = assignee
                else:
                    final_assignee = st.selectbox(
                        "Assignee", options=["(Select)"] + DEVELOPERS, key=assignee_key
                    )
                    if final_assignee == "(Select)":
                        final_assignee = None
                st.markdown("**Issue Type**")
                # Use only valid Jira issue types (exact names)
                issuetype_options = ["Story", "Task", "Bug", "Epic", "Sub-task"]
                default_issuetype = "Story"
                if len(st.session_state.parsed_tasks) > i and st.session_state.parsed_tasks[i].get("issuetype") in issuetype_options:
                    default_issuetype = st.session_state.parsed_tasks[i]["issuetype"]
                selected_issuetype = st.selectbox(
                    "Issue Type",
                    options=issuetype_options,
                    key=issuetype_key,
                    index=issuetype_options.index(default_issuetype)
                )
            st.markdown("**Description**")
            edited_desc = st.text_area("Description", value=description, key=desc_key)
            st.markdown("**Acceptance Criteria**")
            edited_criteria = st.text_area(
                "Acceptance Criteria (one per line)",
                value="\n".join(criteria),
                key=crit_key
            )
            if st.button("Accept", key=accept_key):
                selected_epic_key = selected_epic.split("(")[-1].rstrip(")")
                st.session_state.accepted_tasks.append({
                    "task_name": task_title,
                    "description": edited_desc,
                    "acceptance_criteria": [c.strip() for c in edited_criteria.split("\n") if c.strip()],
                    "assignee": final_assignee,
                    "epic_key": selected_epic_key,
                    "priority_num": priority,
                    "issuetype": selected_issuetype
                })
                st.success(f"Accepted: {task_title}")

def show_configuration() -> None:
    # Initialize config in session state if not present
    if "config" not in st.session_state:
        st.session_state.config = {
            "openai_key": None,
            "epic_mapping": {},
            "is_configured": False
        }
    config = st.session_state.config

    st.markdown('<div style="margin: 0.5rem 0;"><h1 style="color: #6b46c1; font-size: 2.5rem; margin: 0;">AI PRODUCT OWNER</h1></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin: 1rem 0; font-size: 1.5rem;">Configuration</h2>', unsafe_allow_html=True)

    # OpenAI API Key
    api_key = st.text_input(
        "OpenAI API Key:",
        type="password",
        value=config.get("openai_key") or ""
    )

    # Epic Mapping
    st.subheader("Epic Mapping")
    st.markdown("Enter Epic Name → Epic Key mappings. The Epic Key must include the 'AI-' prefix.")
    epic_mapping = config.get("epic_mapping", {})
    col1, col2 = st.columns(2)
    with col1:
        epic_name = st.text_input("Epic Name (e.g., 'Automate VSAT Blockages')")
    with col2:
        epic_key = st.text_input("Full Epic Key (must include 'AI-', e.g., 'AI-285')")
    if st.button("Add Epic Mapping"):
        if epic_name and epic_key:
            if not epic_key.startswith("AI-"):
                st.error("Epic Key must start with 'AI-'. Please enter the complete key (e.g., 'AI-285')")
            else:
                epic_mapping[epic_name] = epic_key
                config["epic_mapping"] = epic_mapping
                st.session_state.config = config
                st.success(f"Added mapping: {epic_name} → {epic_key}")
    # Show current epic mappings
    if epic_mapping:
        st.markdown("### Current Epic Mappings")
        for name, key in epic_mapping.items():
            st.text(f"{name} → {key}")
            if st.button(f"Delete '{name}' mapping", key=f"del_epic_{name}"):
                del epic_mapping[name]
                config["epic_mapping"] = epic_mapping
                st.session_state.config = config
                st.rerun()
    # Show developer mappings (read-only)
    st.subheader("Developer Account IDs (Pre-configured)")
    st.markdown("These are the pre-configured Jira account IDs for each developer:")
    for dev_name, account_id in DEVELOPER_ACCOUNT_IDS.items():
        st.text(f"{dev_name} → {account_id}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save & Return to Main Screen"):
            if not api_key:
                st.error("OpenAI API Key is required!")
                return
            if not epic_mapping:
                st.error("At least one Epic mapping is required!")
                return
            config.update({
                "openai_key": api_key,
                "epic_mapping": epic_mapping,
                "is_configured": True
            })
            st.session_state.config = config
            st.session_state.show_config = False
            st.success("Configuration saved!")
            st.rerun()
    with col2:
        if config.get("is_configured"):
            if st.button("Return to Main Screen (without saving)"):
                st.session_state.show_config = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    return None 