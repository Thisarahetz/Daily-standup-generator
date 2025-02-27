"""
JSON formatter for standup generator output.
"""

import json
import datetime

def format_as_json(standup_speech, commits):
    """
    Format the standup speech and commits as JSON.
    
    Args:
        standup_speech (str): The generated standup speech
        commits (list): List of commit data
    
    Returns:
        str: JSON formatted output
    """
    output = {
        "speech": standup_speech,
        "commits": commits,
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    return json.dumps(output, indent=2)