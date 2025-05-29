import requests
from requests.auth import HTTPBasicAuth
from typing import Tuple, Any, Dict

def inject_tasks_to_jira(jira_url: str, email: str, api_token: str, jira_json: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Injects tasks into Jira Cloud using the bulk issue API.
    Returns (success, response_json)
    """
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/bulk"
    auth = HTTPBasicAuth(email, api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=jira_json, headers=headers, auth=auth)
        response.raise_for_status()
        return True, response.json()
    except requests.HTTPError:
        try:
            return False, response.json()
        except Exception:
            return False, {"error": response.text}
    except Exception as e:
        return False, {"error": str(e)} 