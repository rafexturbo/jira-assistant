import openai
from collections import defaultdict

def add_priorities(tasks):
    """
    Fills 'priority_num' in each task dict.
    tasks[i] must already contain: title, assignee, priority_num (None or 1-5)
    1) leave numbers that came from parser
    2) call GPT-4o once per assignee for missing numbers
    3) return same list with priority_num filled
    """
    # Group tasks by assignee
    assignee_groups = defaultdict(list)
    for idx, task in enumerate(tasks):
        if task.get('priority_num') is None:
            assignee_groups[task.get('assignee')].append((idx, task))
    # For each assignee, call GPT-4o if needed
    for assignee, items in assignee_groups.items():
        if not items:
            continue
        prompt = f"""
Below are the tasks assigned to DEV {assignee}.
Return a JSON mapping "title" → 1-5 priority, making
1 = highest, 5 = lowest. Consider explicit dependencies (before / after) and balance this developer's workload.

Tasks:\n"""
        for _, task in items:
            prompt += f"- {task['title']}\n"
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        # Parse the JSON mapping from the response
        import json
        try:
            mapping = json.loads(response.choices[0].message.content)
        except Exception:
            continue
        for idx, task in items:
            if task['title'] in mapping:
                tasks[idx]['priority_num'] = int(mapping[task['title']])
    return tasks 