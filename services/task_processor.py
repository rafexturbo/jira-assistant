import openai
import re
from typing import List, Dict, Any
import streamlit as st

from config.prompts import ANALYSIS_PROMPT, ENHANCEMENT_PROMPT
from utils.text_utils import match_developer, match_epic
from utils.validation import validate_chatgpt_analysis

def parse_tasks_with_assignees(user_input: str) -> List[Dict[str, Any]]:
    try:
        # First step: Get task analysis with developer and project assignments
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                ANALYSIS_PROMPT,
                {"role": "user", "content": user_input}
            ]
        )
        analyzed_tasks = response.choices[0].message.content

        # Parse developer and project assignments first
        tasks = []
        for task in analyzed_tasks.split('### Task:'):
            if not task.strip():
                continue
            # Extract developer and project from the analyzed tasks
            dev_match = re.search(r'\*\*Developer:\*\* (.*?)(?=\n|\*\*)', task)
            proj_match = re.search(r'\*\*Project:\*\* (.*?)(?=\n|\*\*)', task)
            developer = dev_match.group(1).strip() if dev_match else None
            project = proj_match.group(1).strip() if proj_match else None
            # Match with configured epics
            epic_name = None
            epic_key = None
            if project:
                epic_name = match_epic(project)
                if epic_name and "config" in st.session_state:
                    epic_key = st.session_state.config["epic_mapping"].get(epic_name)
            # Get the original task text
            lines = task.strip().split('\n')
            task_title = lines[0].strip()
            tasks.append({
                "raw_task": task_title,
                "assignee": match_developer(developer) if developer else None,
                "epic_name": epic_name,
                "epic_key": epic_key
            })
        # Second step: Enhance the tasks with descriptions and criteria
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                ENHANCEMENT_PROMPT,
                {"role": "user", "content": analyzed_tasks}
            ]
        )
        enhanced_tasks = response.choices[0].message.content
        # Store the enhanced tasks in the session state
        st.session_state.messages.append({"role": "assistant", "content": enhanced_tasks})
        return tasks
    except Exception as e:
        raise Exception(f"Error processing tasks: {str(e)}") 