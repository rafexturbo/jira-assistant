# Standard Jira Cloud priority IDs (these may need to be updated for your instance)
PRIORITY_MAP = {
    1: "1",  # Highest
    2: "2",  # High
    3: "3",  # Medium
    4: "4",  # Low
    5: "5",  # Lowest
}

def map_number_to_id(priority_num: int) -> str:
    """Map 1-5 to Jira priority id as string."""
    return PRIORITY_MAP.get(priority_num, "3")  # Default to Medium 