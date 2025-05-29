import re
from typing import Dict, Any

from utils.text_utils import match_developer, match_epic

def validate_chatgpt_analysis(response: str) -> Dict[str, Any]:
    try:
        # Split response into tasks
        tasks = response.split("### Task:")
        tasks = [t.strip() for t in tasks if t.strip()]
        
        validated = {
            "tasks": [],
            "developers": []
        }
        
        for task_text in tasks:
            # Extract task details
            task_match = re.search(r"Task: (.*?)(?:\n|$)", task_text)
            developer_match = re.search(r"Developer: (.*?)(?:\n|$)", task_text)
            project_match = re.search(r"Project: (.*?)(?:\n|$)", task_text)
            
            if not all([task_match, developer_match, project_match]):
                continue
                
            task = task_match.group(1).strip()
            developer = developer_match.group(1).strip()
            project = project_match.group(1).strip()
            
            # Validate developer
            matched_developer = match_developer(developer)
            if not matched_developer:
                continue
                
            # Validate project
            matched_project = match_epic(project)
            if not matched_project:
                continue
                
            validated["tasks"].append({
                "text": task,
                "developer": matched_developer,
                "project": matched_project
            })
            
            if matched_developer not in validated["developers"]:
                validated["developers"].append(matched_developer)
                
        return validated
        
    except Exception as e:
        raise Exception(f"Error validating analysis: {str(e)}") 