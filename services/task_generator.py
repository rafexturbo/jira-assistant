from services.task_parser import parse_raw_line
from services.priority_resolver import add_priorities

def generate_tasks_from_input(user_input: str, assignees: list[str]) -> list[dict]:
    """
    Parses user input into tasks, fills priorities, and returns enriched list.
    """
    tasks = []
    for line in user_input.splitlines():
        if not line.strip():
            continue
        priority_num, title = parse_raw_line(line)
        # Assign to first assignee for demo; real logic should assign properly
        assignee = assignees[0] if assignees else None
        tasks.append({
            'title': title,
            'assignee': assignee,
            'priority_num': priority_num
        })
    tasks = add_priorities(tasks)
    return tasks 