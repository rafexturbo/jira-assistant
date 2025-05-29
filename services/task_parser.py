import re

def parse_raw_line(line: str):
    """Returns (priority_num or None, title_without_prefix)"""
    m = re.match(r'^(\d)?\s*(.*)$', line.strip())
    if m:
        num = m.group(1)
        title = m.group(2).strip()
        return (int(num) if num else None, title)
    return (None, line.strip()) 